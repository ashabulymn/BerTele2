"""Scheduler for the Automation Engine (Epic A3).

The scheduler runs registered workflows on a schedule. Schedules are described
declaratively (interval or daily wall-clock) and are evaluated against an
injectable clock so behaviour is fully deterministic in tests.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Any, Protocol

from app.automation.exceptions import AutomationError
from app.automation.workflows import WorkflowExecutor
from app.events.broker import EventBroker
from app.events.event import Event

logger = logging.getLogger("app.automation.scheduler")


# --- Exceptions -----------------------------------------------------------
class ScheduleError(AutomationError):
    """Raised when a scheduled run cannot be evaluated or registered."""


class UnknownScheduleError(ScheduleError):
    """Raised when a schedule name is not registered."""


# --- Domain events --------------------------------------------------------
class ScheduledRunStarted(Event):
    """Emitted when the scheduler begins running a scheduled workflow."""

    def __init__(self, *, schedule_name: str, workflow_name: str, run_id: str) -> None:
        super().__init__(
            name="automation.scheduled_run_started",
            payload={"schedule_name": schedule_name, "workflow_name": workflow_name, "run_id": run_id},
        )


class ScheduledRunCompleted(Event):
    """Emitted when the scheduler finishes running a scheduled workflow."""

    def __init__(self, *, schedule_name: str, workflow_name: str, run_id: str, status: str) -> None:
        super().__init__(
            name="automation.scheduled_run_completed",
            payload={
                "schedule_name": schedule_name,
                "workflow_name": workflow_name,
                "run_id": run_id,
                "status": status,
            },
        )


class ScheduleRegistered(Event):
    """Emitted when a schedule is registered."""

    def __init__(self, *, schedule_name: str, workflow_name: str) -> None:
        super().__init__(
            name="automation.schedule_registered",
            payload={"schedule_name": schedule_name, "workflow_name": workflow_name},
        )


# --- Clock ----------------------------------------------------------------
class Clock(Protocol):
    """Abstraction over time used by the scheduler."""

    def now(self) -> datetime:
        """Return the current UTC datetime."""
        ...


@dataclass(frozen=True, slots=True)
class SystemClock:
    """The real system clock."""

    def now(self) -> datetime:
        from datetime import UTC

        return datetime.now(UTC)


# --- Schedules ------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class IntervalSchedule:
    """Run every ``seconds`` seconds.

    Args:
        seconds: Interval between runs in seconds.
    """

    seconds: float

    def next_after(self, now: datetime) -> datetime:
        return now + timedelta(seconds=self.seconds)

    def run_at(self, now: datetime) -> bool:
        return False


@dataclass(frozen=True, slots=True)
class DailySchedule:
    """Run once per day at ``at`` (UTC).

    Args:
        at: Local wall-clock time of day to run at.
    """

    at: time

    def next_after(self, now: datetime) -> datetime:
        candidate = datetime.combine(now.date(), self.at, tzinfo=now.tzinfo)
        if candidate <= now:
            candidate += timedelta(days=1)
        return candidate

    def run_at(self, now: datetime) -> bool:
        return now.time() == self.at


class Schedule(Protocol):
    """Interface implemented by schedules."""

    def next_after(self, now: datetime) -> datetime:
        """Return the next datetime the schedule should fire at or after ``now``."""
        ...

    def run_at(self, now: datetime) -> bool:
        """Return True when the schedule should run at ``now``."""
        ...


# --- Registry -------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class ScheduledWorkflow:
    """A workflow bound to a schedule.

    Args:
        name: Unique schedule name used for registration.
        workflow_name: Name of the registered workflow to run.
        schedule: The schedule that governs when the workflow runs.
        payload: Static payload merged into each scheduled run.
    """

    name: str
    workflow_name: str
    schedule: Schedule
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScheduleRegistry:
    """Registry of named scheduled workflows."""

    _schedules: dict[str, ScheduledWorkflow] = field(default_factory=dict)

    def register(self, scheduled: ScheduledWorkflow) -> None:
        """Register a scheduled workflow by its name.

        Args:
            scheduled: The scheduled workflow to register.

        Raises:
            ValueError: If a schedule with the same name is already registered.
        """
        if scheduled.name in self._schedules:
            raise ValueError(f"Schedule '{scheduled.name}' is already registered")
        self._schedules[scheduled.name] = scheduled
        logger.info("Registered automation schedule", extra={"schedule_name": scheduled.name})

    def get(self, name: str) -> ScheduledWorkflow:
        """Return a registered scheduled workflow by name.

        Raises:
            UnknownScheduleError: If no schedule with that name is registered.
        """
        try:
            return self._schedules[name]
        except KeyError as exc:
            raise UnknownScheduleError(f"Unknown schedule '{name}'") from exc

    def all(self) -> list[ScheduledWorkflow]:
        """Return all registered scheduled workflows."""
        return list(self._schedules.values())


# --- Scheduler ------------------------------------------------------------
@dataclass
class Scheduler:
    """Runs registered workflows on a schedule.

    Args:
        schedules: Registry of scheduled workflows.
        executor: Executor used to run workflows.
        broker: Optional event broker; when provided, scheduling domain
            events are published for every run.
        clock: Clock used to evaluate schedules; defaults to the real clock.
        interval: Polling interval in seconds used to detect due runs.
    """

    schedules: ScheduleRegistry
    executor: WorkflowExecutor
    broker: EventBroker | None = None
    clock: Clock | None = None
    interval: float = 1.0

    def __post_init__(self) -> None:
        self._clock = self.clock or SystemClock()
        self._task: asyncio.Task[None] | None = None
        self._stop_event: asyncio.Event | None = None
        self._next_run: dict[str, datetime] = {}

    def start(self) -> None:
        """Start the scheduler loop in the current event loop."""
        if self._task is not None and not self._task.done():
            return
        self._stop_event = asyncio.Event()
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        """Stop the scheduler loop and await its completion."""
        if self._stop_event is not None:
            self._stop_event.set()
        if self._task is not None:
            await self._task
        self._task = None
        self._stop_event = None

    async def _run_loop(self) -> None:
        assert self._stop_event is not None
        while True:
            now = self._clock.now()
            for scheduled in self.schedules.all():
                if self._is_due(scheduled, now):
                    await self.run(scheduled.name)
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.interval)
            except asyncio.TimeoutError:
                pass
            if self._stop_event.is_set():
                break

    def _is_due(self, scheduled: ScheduledWorkflow, now: datetime) -> bool:
        last = self._next_run.get(scheduled.name)
        try:
            next_at = scheduled.schedule.next_after(last) if last is not None else now
        except Exception as exc:
            logger.warning(
                "Schedule evaluation failed",
                extra={"schedule_name": scheduled.name, "error": str(exc)},
            )
            return False
        if next_at <= now:
            self._next_run[scheduled.name] = now
            return True
        return False

    async def run(self, schedule_name: str) -> None:
        """Run the workflow bound to a schedule now.

        Args:
            schedule_name: Name of the registered scheduled workflow.
        """
        scheduled = self.schedules.get(schedule_name)
        result = await self.executor.execute(scheduled.workflow_name, scheduled.payload)
        if self.broker is not None:
            await self.broker.publish(
                ScheduledRunCompleted(
                    schedule_name=scheduled.name,
                    workflow_name=scheduled.workflow_name,
                    run_id=result.run_id,
                    status=result.status,
                )
            )

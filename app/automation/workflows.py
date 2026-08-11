"""Workflows, conditions and the workflow executor (Epic A3).

A workflow is a defined sequence of steps. Each step runs an action from the
:class:`~app.automation.actions.ActionRegistry` and may be gated by a condition
from the :class:`ConditionRegistry`. The :class:`WorkflowExecutor` executes a
workflow step by step and publishes domain events for every transition.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Protocol
from uuid import uuid4

from app.automation.actions import ActionRegistry
from app.automation.exceptions import AutomationError
from app.automation.triggers import TriggerRegistry
from app.events.broker import EventBroker
from app.events.event import Event

logger = logging.getLogger("app.automation.workflows")


# --- Exceptions -----------------------------------------------------------
class WorkflowError(AutomationError):
    """Base error for workflow execution."""


class ConditionError(WorkflowError):
    """Raised when a condition cannot be evaluated or registered."""


class UnknownWorkflowError(WorkflowError):
    """Raised when a workflow name is not registered."""


class UnknownConditionError(ConditionError):
    """Raised when a condition name is not registered."""


# --- Domain events --------------------------------------------------------
class WorkflowStarted(Event):
    """Emitted when a workflow run begins."""

    def __init__(self, *, workflow_name: str, run_id: str) -> None:
        super().__init__(
            name="automation.workflow_started",
            payload={"workflow_name": workflow_name, "run_id": run_id},
        )


class WorkflowStepStarted(Event):
    """Emitted when a workflow step begins executing."""

    def __init__(self, *, workflow_name: str, step_name: str, run_id: str) -> None:
        super().__init__(
            name="automation.workflow_step_started",
            payload={"workflow_name": workflow_name, "step_name": step_name, "run_id": run_id},
        )


class WorkflowStepSkipped(Event):
    """Emitted when a workflow step is skipped because its condition failed."""

    def __init__(self, *, workflow_name: str, step_name: str, run_id: str) -> None:
        super().__init__(
            name="automation.workflow_step_skipped",
            payload={"workflow_name": workflow_name, "step_name": step_name, "run_id": run_id},
        )


class WorkflowStepCompleted(Event):
    """Emitted when a workflow step finishes successfully."""

    def __init__(self, *, workflow_name: str, step_name: str, run_id: str, result: dict[str, Any]) -> None:
        super().__init__(
            name="automation.workflow_step_completed",
            payload={
                "workflow_name": workflow_name,
                "step_name": step_name,
                "run_id": run_id,
                "result": result,
            },
        )


class WorkflowStepFailed(Event):
    """Emitted when a workflow step raises an error."""

    def __init__(self, *, workflow_name: str, step_name: str, run_id: str, error: str) -> None:
        super().__init__(
            name="automation.workflow_step_failed",
            payload={
                "workflow_name": workflow_name,
                "step_name": step_name,
                "run_id": run_id,
                "error": error,
            },
        )


class WorkflowCompleted(Event):
    """Emitted when a workflow run finishes all its steps successfully."""

    def __init__(self, *, workflow_name: str, run_id: str, results: list[dict[str, Any]]) -> None:
        super().__init__(
            name="automation.workflow_completed",
            payload={"workflow_name": workflow_name, "run_id": run_id, "results": results},
        )


class WorkflowFailed(Event):
    """Emitted when a workflow run aborts because a step failed."""

    def __init__(self, *, workflow_name: str, run_id: str, error: str) -> None:
        super().__init__(
            name="automation.workflow_failed",
            payload={"workflow_name": workflow_name, "run_id": run_id, "error": error},
        )


# --- Conditions -----------------------------------------------------------
class Condition(Protocol):
    """Interface implemented by workflow conditions."""

    name: str

    def evaluate(self, payload: dict[str, Any]) -> bool:
        """Return True when the step guarded by this condition should run."""
        ...


@dataclass(frozen=True, slots=True)
class FieldEquals:
    """True when ``payload[path]`` equals ``value``.

    Args:
        name: Unique condition name used for registration.
        path: Payload key to inspect.
        value: Expected value.
    """

    name: str
    path: str
    value: Any

    def evaluate(self, payload: dict[str, Any]) -> bool:
        return payload.get(self.path) == self.value


@dataclass(frozen=True, slots=True)
class FieldExists:
    """True when ``payload[path]`` is present and not None.

    Args:
        name: Unique condition name used for registration.
        path: Payload key to inspect.
    """

    name: str
    path: str

    def evaluate(self, payload: dict[str, Any]) -> bool:
        value = payload.get(self.path)
        return value is not None


@dataclass
class ConditionRegistry:
    """Registry of named conditions."""

    _conditions: dict[str, Condition] = field(default_factory=dict)

    def register(self, condition: Condition) -> None:
        """Register a condition by its name.

        Args:
            condition: The condition to register.

        Raises:
            ValueError: If a condition with the same name is already registered.
        """
        if condition.name in self._conditions:
            raise ValueError(f"Condition '{condition.name}' is already registered")
        self._conditions[condition.name] = condition
        logger.info("Registered automation condition", extra={"condition_name": condition.name})

    def get(self, name: str) -> Condition:
        """Return a registered condition by name.

        Raises:
            UnknownConditionError: If no condition with that name is registered.
        """
        try:
            return self._conditions[name]
        except KeyError as exc:
            raise UnknownConditionError(f"Unknown condition '{name}'") from exc

    def all(self) -> list[Condition]:
        """Return all registered conditions."""
        return list(self._conditions.values())


# --- Workflows ------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class WorkflowStep:
    """A single step in a workflow.

    Args:
        name: Unique step name within the workflow.
        action_name: Name of the action to execute (see ``ActionRegistry``).
        condition: Optional name of a condition that gates this step.
        input: Extra payload keys merged over the event payload before the
            action executes. Workflow nodes store only device/chat references;
            connection credentials never appear here.
    """

    name: str
    action_name: str
    condition: str | None = None
    input: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class WorkflowSpec:
    """A defined sequence of steps.

    Args:
        name: Unique workflow name used for registration and scheduling.
        steps: The ordered steps of the workflow.
        description: Optional human-readable description.
    """

    name: str
    steps: tuple[WorkflowStep, ...]
    description: str = ""


@dataclass(frozen=True, slots=True)
class WorkflowRunResult:
    """Outcome of a single workflow run."""

    run_id: str
    workflow_name: str
    status: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


@dataclass
class WorkflowRegistry:
    """Registry of named workflows."""

    _workflows: dict[str, WorkflowSpec] = field(default_factory=dict)

    def register(self, workflow: WorkflowSpec) -> None:
        """Register a workflow by its name.

        Args:
            workflow: The workflow to register.

        Raises:
            ValueError: If a workflow with the same name is already registered.
        """
        if workflow.name in self._workflows:
            raise ValueError(f"Workflow '{workflow.name}' is already registered")
        self._workflows[workflow.name] = workflow
        logger.info("Registered automation workflow", extra={"workflow_name": workflow.name})

    def get(self, name: str) -> WorkflowSpec:
        """Return a registered workflow by name.

        Raises:
            UnknownWorkflowError: If no workflow with that name is registered.
        """
        try:
            return self._workflows[name]
        except KeyError as exc:
            raise UnknownWorkflowError(f"Unknown workflow '{name}'") from exc

    def all(self) -> list[WorkflowSpec]:
        """Return all registered workflows."""
        return list(self._workflows.values())


@dataclass
class WorkflowExecutor:
    """Executes workflows step by step.

    Args:
        workflows: Registry of workflow definitions.
        actions: Registry of actions executed by steps.
        conditions: Registry of conditions gating steps.
        broker: Optional event broker; when provided, workflow domain events
            are published for every transition.
    """

    workflows: WorkflowRegistry
    actions: ActionRegistry
    conditions: ConditionRegistry = field(default_factory=ConditionRegistry)
    broker: EventBroker | None = None

    async def execute(self, workflow_name: str, payload: dict[str, Any]) -> WorkflowRunResult:
        """Run a registered workflow against a payload.

        Steps run in order. A step guarded by a condition is skipped when the
        condition evaluates to False. When a step fails, the run aborts and a
        ``WorkflowFailed`` event (if a broker is present) is published.

        Args:
            workflow_name: Name of the registered workflow to run.
            payload: The event payload that started this run.

        Returns:
            A :class:`WorkflowRunResult` describing the run outcome.
        """
        spec = self.workflows.get(workflow_name)
        run_id = uuid4().hex
        await self._publish(WorkflowStarted(workflow_name=spec.name, run_id=run_id))

        results: list[dict[str, Any]] = []
        for step in spec.steps:
            if step.condition is not None:
                try:
                    gated = self.conditions.get(step.condition).evaluate(payload)
                except ConditionError as exc:
                    return await self._fail(
                        workflow_name=spec.name,
                        run_id=run_id,
                        step_name=step.name,
                        results=results,
                        error=str(exc),
                    )
                if not gated:
                    await self._publish(
                        WorkflowStepSkipped(workflow_name=spec.name, step_name=step.name, run_id=run_id)
                    )
                    results.append({"name": step.name, "status": "skipped"})
                    continue

            await self._publish(
                WorkflowStepStarted(workflow_name=spec.name, step_name=step.name, run_id=run_id)
            )
            try:
                action = self.actions.get(step.action_name)
                result = await action.execute({**payload, **step.input})
            except AutomationError as exc:
                return await self._fail(
                    workflow_name=spec.name,
                    run_id=run_id,
                    step_name=step.name,
                    results=results,
                    error=str(exc),
                )
            await self._publish(
                WorkflowStepCompleted(
                    workflow_name=spec.name, step_name=step.name, run_id=run_id, result=result
                )
            )
            results.append({"name": step.name, "status": "completed", "result": result})

        await self._publish(WorkflowCompleted(workflow_name=spec.name, run_id=run_id, results=results))
        return WorkflowRunResult(run_id=run_id, workflow_name=spec.name, status="completed", steps=results)

    async def _fail(
        self,
        *,
        workflow_name: str,
        run_id: str,
        step_name: str,
        results: list[dict[str, Any]],
        error: str,
    ) -> WorkflowRunResult:
        await self._publish(
            WorkflowStepFailed(workflow_name=workflow_name, step_name=step_name, run_id=run_id, error=error)
        )
        await self._publish(WorkflowFailed(workflow_name=workflow_name, run_id=run_id, error=error))
        self.logger.warning(
            "Workflow step failed",
            extra={"workflow_name": workflow_name, "step_name": step_name, "run_id": run_id, "error": error},
        )
        return WorkflowRunResult(run_id=run_id, workflow_name=workflow_name, status="failed", steps=results, error=error)

    async def _publish(self, event: Event) -> None:
        if self.broker is not None:
            await self.broker.publish(event)

    @property
    def logger(self) -> logging.Logger:
        return logger


@dataclass
class WorkflowManager:
    """Bridges automation trigger events to workflow runs (Epic A3).

    The manager subscribes to the event broker, feeds each incoming event to
    the registered triggers, and runs the workflow bound to each matching
    trigger. It reuses the A2 :class:`~app.automation.triggers.TriggerRegistry`
    and :class:`~app.automation.triggers.EventTrigger`.
    """

    broker: EventBroker
    executor: WorkflowExecutor
    triggers: TriggerRegistry = field(default_factory=TriggerRegistry)
    _binding: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._subscription_name = "automation.workflow_manager"

    def bind(self, trigger, workflow_name: str) -> None:
        """Register a trigger and bind it to a workflow.

        Args:
            trigger: An :class:`~app.automation.triggers.EventTrigger`.
            workflow_name: Name of the registered workflow to run when the
                trigger fires.
        """
        self.triggers.register(trigger)
        self._binding[trigger.name] = workflow_name

    def subscribe(self) -> None:
        """Subscribe the manager to the event broker."""
        self.broker.subscribe(Event, self._on_event, name=self._subscription_name)

    async def _on_event(self, event: Event) -> None:
        """Run the workflow bound to every matching trigger."""
        for trigger in self.triggers.matching(event):
            workflow_name = self._binding.get(trigger.name)
            if workflow_name is None:
                continue
            await self.executor.execute(workflow_name, event.payload)
"""Behavioural tests for the Automation Engine workflows (Epic A3)."""

from __future__ import annotations

import logging
from typing import Any

import pytest

from app.automation.actions import Action, ActionRegistry
from app.automation.exceptions import AutomationError
from app.automation.triggers import EventTrigger, TriggerRegistry
from app.automation.workflows import (
    ConditionRegistry,
    FieldEquals,
    FieldExists,
    UnknownConditionError,
    UnknownWorkflowError,
    WorkflowError,
    WorkflowExecutor,
    WorkflowManager,
    WorkflowRegistry,
    WorkflowSpec,
    WorkflowStep,
)
from app.events import EventBroker
from app.events.event import Event


# --- Helpers --------------------------------------------------------------
class RecordingAction:
    """Action that records every payload it executes."""

    def __init__(self, name: str = "recording.action") -> None:
        self.name = name
        self.calls: list[dict[str, Any]] = []

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(payload)
        return {"called": self.name}


def make_executor(**kwargs) -> WorkflowExecutor:
    """Build a workflow executor with fresh registries."""
    return WorkflowExecutor(
        workflows=WorkflowRegistry(),
        actions=ActionRegistry(),
        conditions=ConditionRegistry(),
        **kwargs,
    )


def sample_workflow(name: str = "w") -> WorkflowSpec:
    return WorkflowSpec(
        name=name,
        steps=(
            WorkflowStep(name="first", action_name="recording.action", input={"step": "first"}),
            WorkflowStep(name="second", action_name="recording.action", input={"step": "second"}),
        ),
    )


# --- Registry -------------------------------------------------------------
def test_workflow_registry_register_get_all() -> None:
    registry = WorkflowRegistry()
    workflow = sample_workflow()
    registry.register(workflow)

    assert registry.get("w") is workflow
    assert registry.all() == [workflow]


def test_workflow_registry_duplicate_raises() -> None:
    registry = WorkflowRegistry()
    registry.register(sample_workflow())

    with pytest.raises(ValueError):
        registry.register(sample_workflow())


def test_workflow_registry_unknown_raises() -> None:
    registry = WorkflowRegistry()

    with pytest.raises(UnknownWorkflowError):
        registry.get("missing")


# --- Conditions -----------------------------------------------------------
def test_field_equals_matches_payload_value() -> None:
    condition = FieldEquals(name="media_is_photo", path="type", value="photo")

    assert condition.evaluate({"type": "photo"}) is True
    assert condition.evaluate({"type": "document"}) is False
    assert condition.evaluate({}) is False


def test_field_exists_matches_payload_value() -> None:
    condition = FieldExists(name="has_session", path="session_id")

    assert condition.evaluate({"session_id": "s-1"}) is True
    assert condition.evaluate({"session_id": None}) is False
    assert condition.evaluate({}) is False


def test_condition_registry_registers_custom_condition() -> None:
    registry = ConditionRegistry()
    condition = FieldEquals(name="media_is_photo", path="type", value="photo")
    registry.register(condition)

    assert registry.get("media_is_photo") is condition
    assert registry.get("media_is_photo").name == "media_is_photo"
    assert registry.all() == [condition]


def test_condition_registry_duplicate_raises() -> None:
    registry = ConditionRegistry()
    registry.register(FieldEquals(name="field_equals", path="type", value="photo"))

    with pytest.raises(ValueError):
        registry.register(FieldEquals(name="field_equals", path="type", value="document"))


def test_condition_registry_unknown_raises() -> None:
    registry = ConditionRegistry()

    with pytest.raises(UnknownConditionError):
        registry.get("missing")


# --- Executor -------------------------------------------------------------
@pytest.mark.anyio
async def test_executor_runs_steps_in_order_with_payload() -> None:
    executor = make_executor()
    action = RecordingAction()
    executor.actions.register(action)
    executor.workflows.register(sample_workflow())

    result = await executor.execute("w", {"event": "data"})

    assert result.workflow_name == "w"
    assert result.status == "completed"
    assert result.error is None
    assert result.run_id
    assert [c["step"] for c in action.calls] == ["first", "second"]
    assert all(c["event"] == "data" for c in action.calls)
    assert [s["name"] for s in result.steps] == ["first", "second"]
    assert all(s["status"] == "completed" for s in result.steps)
    assert result.steps[0]["result"]["called"] == "recording.action"
    assert result.steps[1]["result"]["called"] == "recording.action"


@pytest.mark.anyio
async def test_executor_halts_on_step_failure_and_reports_failure() -> None:
    executor = make_executor()
    first = RecordingAction("first.action")

    class FailingAction(RecordingAction):
        def __init__(self) -> None:
            super().__init__("failing.action")

        async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
            raise WorkflowError("step exploded")

    executor.actions.register(first)
    executor.actions.register(FailingAction())
    executor.workflows.register(
        WorkflowSpec(
            name="w",
            steps=(
                WorkflowStep(name="first", action_name="first.action", input={}),
                WorkflowStep(name="second", action_name="failing.action", input={}),
            ),
        )
    )

    result = await executor.execute("w", {})

    assert result.status == "failed"
    assert result.error == "step exploded"
    assert [s["name"] for s in result.steps] == ["first"]  # halts after failure
    assert len(first.calls) == 1


@pytest.mark.anyio
async def test_executor_skips_step_when_condition_false() -> None:
    executor = make_executor()
    run = RecordingAction("run.action")
    skip = RecordingAction("skip.action")
    executor.actions.register(run)
    executor.actions.register(skip)
    executor.conditions.register(FieldEquals(name="only_photo", path="type", value="photo"))
    executor.workflows.register(
        WorkflowSpec(
            name="w",
            steps=(
                WorkflowStep(name="always", action_name="run.action", input={}),
                WorkflowStep(
                    name="conditional",
                    action_name="skip.action",
                    input={},
                    condition="only_photo",
                ),
            ),
        )
    )

    result = await executor.execute("w", {"type": "document"})

    assert skip.calls == []
    assert result.status == "completed"
    assert [s["name"] for s in result.steps] == ["always", "conditional"]
    assert result.steps[0]["status"] == "completed"
    assert result.steps[1]["status"] == "skipped"


@pytest.mark.anyio
async def test_executor_runs_conditioned_step_when_condition_true() -> None:
    executor = make_executor()
    skip = RecordingAction("skip.action")
    executor.actions.register(skip)
    executor.conditions.register(FieldEquals(name="only_photo", path="type", value="photo"))
    executor.workflows.register(
        WorkflowSpec(
            name="w",
            steps=(
                WorkflowStep(
                    name="conditional",
                    action_name="skip.action",
                    input={},
                    condition="only_photo",
                ),
            ),
        )
    )

    result = await executor.execute("w", {"type": "photo"})

    assert len(skip.calls) == 1
    assert result.status == "completed"
    assert result.steps[0]["status"] == "completed"


@pytest.mark.anyio
async def test_executor_publishes_workflow_domain_events() -> None:
    """The executor must publish domain events for every transition."""
    broker = EventBroker(logger=logging.getLogger("test.automation.workflows"))
    executor = make_executor(broker=broker)
    executor.actions.register(RecordingAction())
    executor.workflows.register(sample_workflow())

    published: list[str] = []
    original_publish = broker.publish

    async def capture(event) -> None:
        published.append(event.name)
        await original_publish(event)

    broker.publish = capture  # type: ignore[method-assign]

    await executor.execute("w", {})

    assert published == [
        "automation.workflow_started",
        "automation.workflow_step_started",
        "automation.workflow_step_completed",
        "automation.workflow_step_started",
        "automation.workflow_step_completed",
        "automation.workflow_completed",
    ]


@pytest.mark.anyio
async def test_executor_publishes_workflow_failed_event_on_error() -> None:
    broker = EventBroker(logger=logging.getLogger("test.automation.workflows"))
    executor = make_executor(broker=broker)

    class FailingAction(RecordingAction):
        async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
            raise WorkflowError("boom")

    executor.actions.register(FailingAction("failing.action"))
    executor.workflows.register(
        WorkflowSpec(
            name="w",
            steps=(WorkflowStep(name="only", action_name="failing.action", input={}),),
        )
    )

    published: list[str] = []
    original_publish = broker.publish

    async def capture(event) -> None:
        published.append(event.name)
        await original_publish(event)

    broker.publish = capture  # type: ignore[method-assign]

    result = await executor.execute("w", {})

    assert result.status == "failed"
    assert published[-2:] == ["automation.workflow_step_failed", "automation.workflow_failed"]


# --- Manager --------------------------------------------------------------
@pytest.mark.anyio
async def test_workflow_manager_binds_trigger_to_workflow_and_runs_on_event() -> None:
    broker = EventBroker(logger=logging.getLogger("test.automation.workflows"))
    executor = make_executor(broker=broker)
    action = RecordingAction()
    executor.actions.register(action)
    executor.workflows.register(sample_workflow())

    manager = WorkflowManager(broker=broker, executor=executor)
    manager.bind(EventTrigger(name="on-created", event_name="media.created"), "w")

    await manager._on_event(Event(name="media.created", payload={"media_id": "m-1"}))

    # One workflow run with two steps; the event payload flows into both steps.
    assert len(action.calls) == 2
    assert all(call["media_id"] == "m-1" for call in action.calls)


@pytest.mark.anyio
async def test_workflow_manager_ignores_non_matching_events() -> None:
    broker = EventBroker(logger=logging.getLogger("test.automation.workflows"))
    executor = make_executor()
    action = RecordingAction()
    executor.actions.register(action)
    executor.workflows.register(sample_workflow())

    manager = WorkflowManager(broker=broker, executor=executor)
    manager.bind(EventTrigger(name="on-created", event_name="media.created"), "w")

    await manager._on_event(Event(name="media.deleted", payload={}))

    assert action.calls == []

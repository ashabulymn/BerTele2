"""Automation Engine — triggers, actions, workflows and scheduling (Epics A2/A3).

This package provides the Automation Engine foundation:

- ``Trigger`` / ``TriggerRegistry`` — detect domain events (Epic A2).
- ``Action`` / ``ActionRegistry`` — execute side effects (e.g. GoWA media send) (Epic A2).
- ``AutomationEngine`` — subscribes to the event broker, fires triggers and
  runs the actions bound to each trigger (Epic A2).
- ``Workflow`` / ``WorkflowRegistry`` / ``WorkflowExecutor`` — run ordered
  action sequences gated by conditions (Epic A3).
- ``Scheduler`` / ``ScheduleRegistry`` — run workflows on a schedule (Epic A3).
"""

from app.automation.actions import Action, ActionRegistry, GoWASendMediaAction
from app.automation.engine import AutomationEngine
from app.automation.events import (
    AutomationActionCompleted,
    AutomationActionFailed,
    AutomationActionStarted,
    AutomationTriggered,
)
from app.automation.exceptions import (
    ActionError,
    AutomationError,
    TriggerError,
    UnknownActionError,
    UnknownTriggerError,
)
from app.automation.scheduler import (
    DailySchedule,
    IntervalSchedule,
    ScheduleError,
    ScheduleRegistry,
    ScheduledRunCompleted,
    ScheduledRunStarted,
    ScheduledWorkflow,
    Scheduler,
    UnknownScheduleError,
)
from app.automation.triggers import EventTrigger, Trigger, TriggerRegistry
from app.automation.workflows import (
    ConditionError,
    ConditionRegistry,
    FieldEquals,
    FieldExists,
    UnknownConditionError,
    UnknownWorkflowError,
    WorkflowCompleted,
    WorkflowError,
    WorkflowExecutor,
    WorkflowFailed,
    WorkflowManager,
    WorkflowRegistry,
    WorkflowRunResult,
    WorkflowSpec,
    WorkflowStarted,
    WorkflowStep,
    WorkflowStepCompleted,
    WorkflowStepFailed,
    WorkflowStepSkipped,
    WorkflowStepStarted,
)

__all__ = [
    "Action",
    "ActionError",
    "ActionRegistry",
    "AutomationActionCompleted",
    "AutomationActionFailed",
    "AutomationActionStarted",
    "AutomationEngine",
    "AutomationError",
    "AutomationTriggered",
    "ConditionError",
    "ConditionRegistry",
    "DailySchedule",
    "EventTrigger",
    "FieldEquals",
    "FieldExists",
    "GoWASendMediaAction",
    "IntervalSchedule",
    "ScheduleError",
    "ScheduleRegistry",
    "ScheduledRunCompleted",
    "ScheduledRunStarted",
    "ScheduledWorkflow",
    "Scheduler",
    "Trigger",
    "TriggerError",
    "TriggerRegistry",
    "UnknownActionError",
    "UnknownConditionError",
    "UnknownScheduleError",
    "UnknownTriggerError",
    "UnknownWorkflowError",
    "WorkflowCompleted",
    "WorkflowError",
    "WorkflowExecutor",
    "WorkflowFailed",
    "WorkflowManager",
    "WorkflowRegistry",
    "WorkflowRunResult",
    "WorkflowSpec",
    "WorkflowStarted",
    "WorkflowStep",
    "WorkflowStepCompleted",
    "WorkflowStepFailed",
    "WorkflowStepSkipped",
    "WorkflowStepStarted",
]
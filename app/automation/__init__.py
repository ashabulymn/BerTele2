"""Automation Engine — triggers and actions (Epic A2).

This package provides the foundation of the Automation Engine:

- ``Trigger`` / ``TriggerRegistry`` — detect domain events.
- ``Action`` / ``ActionRegistry`` — execute side effects (e.g. GoWA media send).
- ``AutomationEngine`` — subscribes to the event broker, fires triggers and
  runs the actions bound to each trigger.

Scheduling, workflows and conditions are intentionally out of scope for this
epic and will be delivered by Epic A3.
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
from app.automation.triggers import EventTrigger, Trigger, TriggerRegistry

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
    "EventTrigger",
    "GoWASendMediaAction",
    "Trigger",
    "TriggerError",
    "TriggerRegistry",
    "UnknownActionError",
    "UnknownTriggerError",
]
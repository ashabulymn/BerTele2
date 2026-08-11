"""Exceptions for the Automation Engine (Epic A2)."""

from __future__ import annotations


class AutomationError(Exception):
    """Base error for the automation engine."""


class TriggerError(AutomationError):
    """Raised when a trigger cannot be evaluated or registered."""


class ActionError(AutomationError):
    """Raised when an action fails to execute."""


class UnknownTriggerError(TriggerError):
    """Raised when a trigger name is not registered."""


class UnknownActionError(ActionError):
    """Raised when an action name is not registered."""
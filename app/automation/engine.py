"""Automation Engine — triggers and actions (Epic A2).

The engine subscribes to the event broker, feeds each incoming event to the
registered triggers, and runs the actions bound to each matching trigger.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from uuid import uuid4

from app.automation.actions import ActionRegistry
from app.automation.events import (
    AutomationActionCompleted,
    AutomationActionFailed,
    AutomationActionStarted,
    AutomationTriggered,
)
from app.automation.exceptions import ActionError
from app.automation.triggers import TriggerRegistry
from app.events.broker import EventBroker
from app.events.event import Event

logger = logging.getLogger("app.automation.engine")


@dataclass
class AutomationEngine:
    """Coordinates triggers and actions.

    Args:
        broker: The event broker the engine subscribes to.
        triggers: Registry of triggers.
        actions: Registry of actions.
        logger: Optional logger override.
    """

    broker: EventBroker
    triggers: TriggerRegistry = field(default_factory=TriggerRegistry)
    actions: ActionRegistry = field(default_factory=ActionRegistry)
    logger: logging.Logger = field(default_factory=lambda: logging.getLogger("app.automation.engine"))

    def __post_init__(self) -> None:
        self._subscription_name = "automation.engine"

    def subscribe(self) -> None:
        """Subscribe the engine to the event broker."""
        self.broker.subscribe(Event, self._on_event, name=self._subscription_name)
        self.logger.info("Automation engine subscribed to event broker")

    async def _on_event(self, event: Event) -> None:
        """Handle an incoming event from the broker."""
        for trigger in self.triggers.matching(event):
            await self._fire(trigger.name, event)

    async def _fire(self, trigger_name: str, event: Event) -> None:
        """Run the actions bound to a trigger."""
        await self.broker.publish(
            AutomationTriggered(trigger_name=trigger_name, event_name=event.name, payload=event.payload)
        )
        for action in self.actions.all():
            run_id = uuid4().hex
            await self.broker.publish(
                AutomationActionStarted(trigger_name=trigger_name, action_name=action.name, run_id=run_id)
            )
            try:
                result = await action.execute(event.payload)
            except ActionError as exc:
                await self.broker.publish(
                    AutomationActionFailed(
                        trigger_name=trigger_name,
                        action_name=action.name,
                        run_id=run_id,
                        error=str(exc),
                    )
                )
                self.logger.warning(
                    "Automation action failed",
                    extra={
                        "trigger_name": trigger_name,
                        "action_name": action.name,
                        "run_id": run_id,
                        "error": str(exc),
                    },
                )
                continue
            except Exception as exc:
                await self.broker.publish(
                    AutomationActionFailed(
                        trigger_name=trigger_name,
                        action_name=action.name,
                        run_id=run_id,
                        error=str(exc),
                    )
                )
                self.logger.exception(
                    "Unexpected automation action error",
                    extra={
                        "trigger_name": trigger_name,
                        "action_name": action.name,
                        "run_id": run_id,
                    },
                )
                continue
            await self.broker.publish(
                AutomationActionCompleted(
                    trigger_name=trigger_name,
                    action_name=action.name,
                    run_id=run_id,
                    result=result,
                )
            )
            self.logger.info(
                "Automation action completed",
                extra={
                    "trigger_name": trigger_name,
                    "action_name": action.name,
                    "run_id": run_id,
                },
            )
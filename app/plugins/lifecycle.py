from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.plugins.exceptions import PluginLifecycleError


class PluginState(str, Enum):
    PENDING = "pending"
    LOADED = "loaded"
    STARTING = "starting"
    STARTED = "started"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass(slots=True)
class PluginLifecycle:
    state: PluginState = field(default=PluginState.PENDING)

    def transition(self, next_state: PluginState) -> PluginState:
        allowed = {
            PluginState.PENDING: {PluginState.LOADED, PluginState.ERROR},
            PluginState.LOADED: {PluginState.STARTING, PluginState.STOPPED, PluginState.ERROR},
            PluginState.STARTING: {PluginState.STARTED, PluginState.ERROR},
            PluginState.STARTED: {PluginState.STOPPING, PluginState.ERROR},
            PluginState.STOPPING: {PluginState.STOPPED, PluginState.ERROR},
            PluginState.STOPPED: {PluginState.LOADED, PluginState.ERROR},
            PluginState.ERROR: {PluginState.LOADED, PluginState.STOPPED},
        }
        if next_state not in allowed.get(self.state, set()):
            raise PluginLifecycleError(
                f"Invalid lifecycle transition from {self.state.value} to {next_state.value}"
            )
        self.state = next_state
        return self.state

    @property
    def active(self) -> bool:
        return self.state is PluginState.STARTED

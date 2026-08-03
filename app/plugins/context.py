from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from app.events import Event
from app.events.subscriber import EventSubscriber
from app.plugins.exceptions import PluginConfigurationError, PluginDependencyError
from app.plugins.manifest import PluginManifest


class SupportsPublish(Protocol):
    async def publish(self, event: Event) -> None: ...


@dataclass(slots=True)
class PluginConfig:
    values: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.values[key] = value

    def update(self, values: Mapping[str, Any]) -> None:
        self.values.update(dict(values))

    def as_dict(self) -> dict[str, Any]:
        return dict(self.values)


class DependencyInjector:
    def __init__(self, services: Mapping[str, Any] | None = None) -> None:
        self._services: dict[str, Any] = dict(services or {})

    def register(self, name: str, value: Any) -> None:
        self._services[name] = value

    def resolve(self, name: str, default: Any = None) -> Any:
        if name in self._services:
            return self._services[name]
        if default is not None:
            return default
        raise PluginDependencyError(f"Dependency {name!r} is not registered")

    def get(self, name: str, default: Any = None) -> Any:
        return self._services.get(name, default)


@dataclass(slots=True)
class PluginContext:
    manifest: PluginManifest
    config: PluginConfig = field(default_factory=PluginConfig)
    logger: logging.Logger = field(default_factory=lambda: logging.getLogger("app.plugins"))
    broker: EventSubscriber | SupportsPublish | None = None
    injector: DependencyInjector = field(default_factory=DependencyInjector)
    metadata: dict[str, Any] = field(default_factory=dict)

    def register_service(self, name: str, value: Any) -> None:
        self.injector.register(name, value)

    def require_service(self, name: str, default: Any = None) -> Any:
        return self.injector.resolve(name, default)

    def subscribe(self, event_type: type[Event], handler: object, *, name: str | None = None) -> None:
        if self.broker is None:
            raise PluginConfigurationError("No internal event broker configured for plugin context")
        if not hasattr(self.broker, "subscribe"):
            raise PluginConfigurationError("Configured broker does not support subscription")
        self.broker.subscribe(event_type, handler, name=name)

    async def emit(self, event: Event) -> None:
        if self.broker is None:
            raise PluginConfigurationError("No internal event broker configured for plugin context")
        if not hasattr(self.broker, "publish"):
            raise PluginConfigurationError("Configured broker does not support publishing")
        await self.broker.publish(event)

    def set_config(self, key: str, value: Any) -> None:
        self.config.set(key, value)

    def get_config(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def merge_config(self, values: Mapping[str, Any]) -> None:
        self.config.update(values)

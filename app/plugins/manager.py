from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from app.events import Event
from app.events.subscriber import EventSubscriber
from app.plugins.exceptions import PluginLoadError, PluginVersionError
from app.plugins.hooks import HookRegistry
from app.plugins.loader import PluginLoader
from app.plugins.registry import PluginRegistry


@dataclass(slots=True)
class ReloadHandle:
    plugin_id: str
    manager: PluginManager

    def reload(self) -> Any:
        return self.manager.reload_plugin(self.plugin_id)

    def stop(self) -> None:
        self.manager.stop_plugin(self.plugin_id)


class PluginManager:
    def __init__(
        self,
        *,
        event_broker: EventSubscriber | None = None,
        registry: PluginRegistry | None = None,
        loader: PluginLoader | None = None,
        logger: logging.Logger | None = None,
        hooks: HookRegistry | None = None,
    ) -> None:
        self.event_broker = event_broker
        self.registry = registry or PluginRegistry()
        self.loader = loader or PluginLoader(self.registry)
        self.logger = logger or logging.getLogger("app.plugins")
        self.hooks = hooks or HookRegistry()

    def subscribe(self, event_type: type[Event], handler: Any, *, name: str | None = None) -> None:
        if self.event_broker is None:
            raise PluginLoadError("Plugin manager has no internal event broker configured")
        self.event_broker.subscribe(event_type, handler, name=name)

    def load(self, plugin_path: str, *, config: dict[str, Any] | None = None) -> Any:
        plugin = self.loader.load_plugin(
            plugin_path,
            config=config,
            event_broker=self.event_broker,
            logger=self.logger,
        )
        self.hooks.dispatch("plugin.loaded", plugin)
        return plugin

    async def start(self, plugin_id: str | None = None) -> None:
        plugins = self.registry.list() if plugin_id is None else [self.registry.get(plugin_id)]
        for plugin in plugins:
            if plugin is None:
                continue
            if not plugin.manifest.is_compatible("0.0.0"):
                raise PluginVersionError(f"Plugin {plugin.plugin_id} is incompatible with application version")
            await plugin.on_start()
            self.hooks.dispatch("plugin.started", plugin)

    async def stop_plugin(self, plugin_id: str) -> None:
        plugin = self.registry.get(plugin_id)
        if plugin is None:
            return
        await plugin.on_stop()
        self.hooks.dispatch("plugin.stopped", plugin)

    def reload_plugin(self, plugin_id: str) -> Any:
        plugin = self.registry.get(plugin_id)
        if plugin is None:
            raise PluginLoadError(f"Plugin {plugin_id} is not registered")
        hot_reload = ReloadHandle(plugin_id=plugin_id, manager=self)
        self.hooks.dispatch("plugin.reload_requested", plugin, hot_reload)
        return hot_reload

    def get_plugin(self, plugin_id: str) -> Any:
        return self.registry.get(plugin_id)

    def list_plugins(self) -> list[Any]:
        return self.registry.list()

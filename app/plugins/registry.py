from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from app.plugins.exceptions import PluginLoadError

if TYPE_CHECKING:
    from app.plugins.base import PluginBase


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, PluginBase] = {}

    def register(self, plugin: PluginBase) -> PluginBase:
        plugin_id = getattr(plugin, "plugin_id", None) or getattr(plugin, "manifest", None).plugin_id
        if not plugin_id:
            raise PluginLoadError("Plugin must define a plugin_id before registration")
        self._plugins[plugin_id] = plugin
        return plugin

    def unregister(self, plugin_id: str) -> None:
        self._plugins.pop(plugin_id, None)

    def get(self, plugin_id: str, default: Any = None) -> PluginBase | Any:
        return self._plugins.get(plugin_id, default)

    def __contains__(self, plugin_id: str) -> bool:
        return plugin_id in self._plugins

    def __iter__(self) -> Iterator[str]:
        return iter(self._plugins)

    def list(self) -> list[PluginBase]:
        return list(self._plugins.values())

    def clear(self) -> None:
        self._plugins.clear()

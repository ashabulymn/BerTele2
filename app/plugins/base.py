from __future__ import annotations

import inspect
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from app.events import Event
from app.plugins.context import PluginContext
from app.plugins.exceptions import PluginConfigurationError, PluginLifecycleError
from app.plugins.lifecycle import PluginLifecycle, PluginState
from app.plugins.manifest import PluginManifest


class PluginBase(ABC):
    def __init__(
        self,
        *,
        manifest: PluginManifest,
        context: PluginContext | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.manifest = manifest
        self.context = context or PluginContext(
            manifest=manifest,
            logger=logger or logging.getLogger("app.plugins"),
        )
        self.lifecycle = PluginLifecycle()

    @property
    def plugin_id(self) -> str:
        return self.manifest.plugin_id

    @property
    def name(self) -> str:
        return self.manifest.name

    @property
    def version(self) -> str:
        return self.manifest.version

    def validate_config(self) -> None:
        if self.context.config is None:
            raise PluginConfigurationError(f"Plugin {self.plugin_id} configuration is missing")

    def subscribe(self, event_type: type[Event], handler: Callable[..., Any], *, name: str | None = None) -> None:
        self.context.subscribe(event_type, handler, name=name)

    async def emit(self, event: Event) -> None:
        await self.context.emit(event)

    def register_hook(self, hook_name: str, callback: Callable[..., Any], **kwargs: Any) -> object:
        if not hasattr(self, "hooks"):
            raise PluginLifecycleError("Plugin does not define a hook registry")
        return self.hooks.register(hook_name, callback, **kwargs)

    def is_compatible(self, app_version: str) -> bool:
        return self.manifest.is_compatible(app_version)

    def supports_version(self, app_version: str) -> bool:
        return self.is_compatible(app_version)

    def version_compatible_with(self, app_version: str) -> bool:
        return self.is_compatible(app_version)

    async def _run_hook(self, method_name: str) -> None:
        hook = getattr(self, method_name, None)
        if hook is None:
            return
        result = hook()
        if inspect.isawaitable(result):
            await result

    async def on_load(self) -> None:
        self.lifecycle.transition(PluginState.LOADED)

    async def on_start(self) -> None:
        self.lifecycle.transition(PluginState.STARTING)
        await self._run_hook("start")
        self.lifecycle.transition(PluginState.STARTED)

    async def on_stop(self) -> None:
        self.lifecycle.transition(PluginState.STOPPING)
        await self._run_hook("stop")
        self.lifecycle.transition(PluginState.STOPPED)

    async def on_reload(self) -> None:
        await self.on_stop()
        await self.on_start()

    @classmethod
    @abstractmethod
    def build_manifest(cls) -> PluginManifest:
        raise NotImplementedError

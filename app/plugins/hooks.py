from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class PluginHook:
    name: str
    callback: Callable[..., Any]
    priority: int = 0
    plugin_id: str | None = None
    once: bool = False


class HookRegistry:
    def __init__(self) -> None:
        self._hooks: dict[str, list[PluginHook]] = defaultdict(list)

    def register(
        self,
        hook_name: str,
        callback: Callable[..., Any],
        *,
        priority: int = 0,
        plugin_id: str | None = None,
        once: bool = False,
    ) -> PluginHook:
        hook = PluginHook(
            name=hook_name,
            callback=callback,
            priority=priority,
            plugin_id=plugin_id,
            once=once,
        )
        self._hooks[hook_name].append(hook)
        return hook

    def dispatch(self, hook_name: str, *args: Any, **kwargs: Any) -> list[Any]:
        results: list[Any] = []
        for hook in sorted(self._hooks.get(hook_name, []), key=lambda item: item.priority, reverse=True):
            results.append(hook.callback(*args, **kwargs))
            if hook.once:
                self._hooks[hook_name].remove(hook)
        return results

    def clear(self, hook_name: str | None = None) -> None:
        if hook_name is None:
            self._hooks.clear()
            return
        self._hooks.pop(hook_name, None)

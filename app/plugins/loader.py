from __future__ import annotations

import importlib
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any

from app.plugins.base import PluginBase
from app.plugins.context import PluginConfig, PluginContext
from app.plugins.exceptions import PluginLoadError, PluginManifestError
from app.plugins.manifest import PluginManifest
from app.plugins.registry import PluginRegistry


class PluginLoader:
    def __init__(self, registry: PluginRegistry | None = None) -> None:
        self.registry = registry or PluginRegistry()

    def load_manifest(self, plugin_path: str | Path) -> PluginManifest:
        plugin_dir = Path(plugin_path)
        if plugin_dir.is_file():
            plugin_dir = plugin_dir.parent

        candidates = [
            plugin_dir / "manifest.json",
            plugin_dir / "plugin.json",
            plugin_dir / "manifest.toml",
            plugin_dir / "plugin.toml",
        ]
        for candidate in candidates:
            if candidate.exists():
                return PluginManifest.from_file(candidate)
        raise PluginManifestError(f"No plugin manifest found for {plugin_dir}")

    def _load_module_from_file(self, module_name: str, file_path: Path) -> Any:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise PluginLoadError(f"Unable to create import spec for {file_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def _load_plugin_class(self, manifest: PluginManifest, plugin_root: Path) -> type[PluginBase]:
        entrypoint = manifest.entrypoint
        if ":" in entrypoint:
            module_name, class_name = entrypoint.split(":", 1)
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, class_name)
            if not isinstance(plugin_class, type):
                raise PluginLoadError(f"Entrypoint {entrypoint!r} did not resolve to a class")
            if not issubclass(plugin_class, PluginBase):
                raise PluginLoadError(f"Plugin class {plugin_class!r} must inherit from PluginBase")
            return plugin_class

        if entrypoint.endswith(".py"):
            file_path = (plugin_root / entrypoint).resolve()
            module_name = f"bertele_plugin_{file_path.stem}_{abs(hash(file_path))}"
            module = self._load_module_from_file(module_name, file_path)
            candidates = [
                obj
                for _, obj in inspect.getmembers(module, inspect.isclass)
                if issubclass(obj, PluginBase) and obj is not PluginBase
            ]
            if not candidates:
                raise PluginLoadError(f"No PluginBase subclass found in {file_path}")
            return candidates[0]

        module_name, class_name = entrypoint.rsplit(".", 1)
        module = importlib.import_module(module_name)
        plugin_class = getattr(module, class_name)
        if not isinstance(plugin_class, type):
            raise PluginLoadError(f"Entrypoint {entrypoint!r} did not resolve to a class")
        if not issubclass(plugin_class, PluginBase):
            raise PluginLoadError(f"Plugin class {plugin_class!r} must inherit from PluginBase")
        return plugin_class

    def load_plugin(
        self,
        plugin_path: str | Path,
        *,
        config: dict[str, Any] | None = None,
        event_broker: Any = None,
        logger: Any = None,
    ) -> PluginBase:
        plugin_root = Path(plugin_path)
        manifest = self.load_manifest(plugin_root)
        plugin_class = self._load_plugin_class(manifest, plugin_root if plugin_root.is_dir() else plugin_root.parent)

        context = PluginContext(
            manifest=manifest,
            config=PluginConfig(dict(manifest.config) | (config or {})),
            logger=logger,
            broker=event_broker,
        )
        plugin = plugin_class(manifest=manifest, context=context, logger=logger)
        self.registry.register(plugin)
        return plugin

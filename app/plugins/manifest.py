from __future__ import annotations

import json
import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.plugins.exceptions import PluginManifestError, PluginVersionError


def _normalize_version(value: str) -> tuple[int, ...]:
    digits = tuple(int(part) for part in re.findall(r"\d+", str(value)))
    if not digits:
        raise PluginVersionError(f"Unsupported version string: {value!r}")
    return digits


def _compare_versions(left: str, right: str) -> int:
    left_version = _normalize_version(left)
    right_version = _normalize_version(right)
    max_length = max(len(left_version), len(right_version))
    padded_left = left_version + (0,) * (max_length - len(left_version))
    padded_right = right_version + (0,) * (max_length - len(right_version))
    if padded_left < padded_right:
        return -1
    if padded_left > padded_right:
        return 1
    return 0


@dataclass(frozen=True, slots=True)
class PluginManifest:
    plugin_id: str
    name: str
    version: str
    entrypoint: str
    description: str = ""
    author: str | None = None
    requires: tuple[str, ...] = ()
    compatibility: dict[str, str] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    min_app_version: str | None = None
    max_app_version: str | None = None

    def __post_init__(self) -> None:
        self.validate()

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> PluginManifest:
        raw_config = payload.get("config", {})
        enough = {
            "plugin_id": payload.get("plugin_id") or payload.get("id"),
            "name": payload.get("name"),
            "version": payload.get("version"),
            "entrypoint": payload.get("entrypoint") or payload.get("module"),
            "description": payload.get("description", ""),
            "author": payload.get("author"),
            "requires": tuple(payload.get("requires", ())),
            "compatibility": dict(payload.get("compatibility", {})),
            "config": dict(raw_config),
            "min_app_version": payload.get("min_app_version")
            or payload.get("minimum_app_version"),
            "max_app_version": payload.get("max_app_version")
            or payload.get("maximum_app_version"),
        }
        return cls(**enough)

    @classmethod
    def from_file(cls, path: str | Path) -> PluginManifest:
        file_path = Path(path)
        if not file_path.exists():
            raise PluginManifestError(f"Manifest file not found: {file_path}")

        if file_path.suffix == ".json":
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        elif file_path.suffix in {".toml", ".tml"}:
            payload = tomllib.loads(file_path.read_text(encoding="utf-8"))
        else:
            raise PluginManifestError(f"Unsupported manifest format: {file_path}")

        if not isinstance(payload, dict):
            raise PluginManifestError("Manifest payload must be a dictionary")
        return cls.from_dict(payload)

    def validate(self) -> None:
        if not self.plugin_id:
            raise PluginManifestError("Plugin manifest is missing plugin_id")
        if not self.name:
            raise PluginManifestError("Plugin manifest is missing name")
        if not self.version:
            raise PluginManifestError("Plugin manifest is missing version")
        if not self.entrypoint:
            raise PluginManifestError("Plugin manifest is missing entrypoint")

        _normalize_version(self.version)
        if self.min_app_version is not None:
            _normalize_version(self.min_app_version)
        if self.max_app_version is not None:
            _normalize_version(self.max_app_version)

    def supports_version(self, app_version: str) -> bool:
        if self.min_app_version is not None and _compare_versions(app_version, self.min_app_version) < 0:
            return False
        return not (
            self.max_app_version is not None and _compare_versions(app_version, self.max_app_version) > 0
        )

    def is_compatible(self, app_version: str) -> bool:
        return self.supports_version(app_version)

    def version_compatible_with(self, app_version: str) -> bool:
        return self.supports_version(app_version)

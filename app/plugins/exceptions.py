from __future__ import annotations


class PluginError(RuntimeError):
    """Base error for plugin SDK failures."""


class PluginLoadError(PluginError):
    """Raised when a plugin cannot be loaded."""


class PluginManifestError(PluginError):
    """Raised when a plugin manifest is invalid."""


class PluginConfigurationError(PluginError):
    """Raised when plugin configuration is invalid."""


class PluginDependencyError(PluginError):
    """Raised when a plugin dependency is missing or invalid."""


class PluginVersionError(PluginError):
    """Raised when plugin version compatibility checks fail."""


class PluginLifecycleError(PluginError):
    """Raised when a plugin lifecycle transition is invalid."""

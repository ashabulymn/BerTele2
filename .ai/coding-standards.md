# BerTele2 Coding Standards

This document defines the coding standards for the BerTele2 project. All code must follow these conventions.

## Python Style

- Follow **PEP 8**.
- Use **4 spaces** for indentation (no tabs).
- Use **double quotes** for strings.
- Use **`from __future__ import annotations`** at the top of every module.
- Use **`snake_case`** for functions, methods, and variables.
- Use **`PascalCase`** for classes.
- Use **`UPPER_SNAKE_CASE`** for constants.
- Use **`slots=True`** in dataclasses where appropriate for performance.

## Naming Conventions

| Item | Convention | Example |
| --- | --- | --- |
| Module | `snake_case` | `message_pipeline.py` |
| Class | `PascalCase` | `MessagePipeline` |
| Function | `snake_case` | `register_handler` |
| Method | `snake_case` | `dispatch` |
| Variable | `snake_case` | `session_id` |
| Constant | `UPPER_SNAKE_CASE` | `DEFAULT_PIPELINE_STEPS` |
| Private | leading underscore | `_clients` |
| Type alias | `PascalCase` | `PipelineHandler` |

## Typing

- Use **type hints** on all function signatures and public attributes.
- Use **`from __future__ import annotations`** to defer evaluation.
- Use **`typing`** generics: `list[T]`, `dict[K, V]`, `tuple[...]`, `set[T]`.
- Use **`Optional[T]`** or **`T | None`** (prefer `T | None`).
- Use **`Any`** sparingly; prefer precise types.
- Use **`Protocol`** for structural typing where appropriate.
- Use **`TypeVar`** for generic functions.

## Docstrings

- Use **Google style** docstrings.
- Document the **purpose**, **Args**, **Returns**, and **Raises**.
- Keep docstrings concise and accurate.

```python
def send_media(self, resource: MediaResource, recipient: str) -> dict[str, Any]:
    """Send a media resource to a recipient.

    Args:
        resource: The media resource from the pipeline.
        recipient: The recipient identifier.

    Returns:
        A dictionary with delivery result information.

    Raises:
        GoWAValidationError: If the resource or configuration is invalid.
    """
```

## Logging

- Use the **`logging`** module.
- Get a logger per module: `logger = logging.getLogger(__name__)`.
- Use **structured extra** fields for context.
- Log at appropriate levels: `debug`, `info`, `warning`, `error`, `exception`.
- Do **not** log secrets, tokens, or passwords.

```python
self.logger.info(
    "Incoming Telegram message",
    extra={"session_id": context.session_id, "message_id": message_id},
)
```

## Dependency Injection

- Use **constructor injection** for all services.
- Dependencies are passed as constructor arguments.
- Use **`dataclass`** or explicit `__init__` for wiring.
- Avoid global singletons and module-level mutable state.
- Use the container (`app/core/container.py`) for composition root.

See [decisions/ADR-0006-dependency-injection.md](decisions/ADR-0006-dependency-injection.md).

## Error Handling

- Define **domain-specific exceptions** in each subsystem.
- Raise exceptions with **clear messages**.
- Catch exceptions at **boundaries** (API, pipeline, worker).
- Use **`raise ... from exc`** to preserve context.
- Do **not** swallow exceptions silently.

## Folder Conventions

- Each subsystem lives under `app/<subsystem>/`.
- Public API is exported via the subsystem's `__init__.py`.
- Tests live under `tests/<subsystem>/`.
- Connectors/plugins live under `plugins/<name>/`.

## Testing Conventions

- Use **pytest**.
- Name test files `test_<module>.py`.
- Name test functions `test_<behavior>`.
- Use **fixtures** for shared setup.
- Mock external dependencies (Telethon, HTTP).
- Aim for **high coverage** of public behavior.

See [testing.md](testing.md).

---

## Related Documents

- [development-rules.md](development-rules.md) — Mandatory rules.
- [testing.md](testing.md) — Testing strategy.
- [review-checklist.md](review-checklist.md) — Review checklist.
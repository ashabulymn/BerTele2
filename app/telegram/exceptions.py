from __future__ import annotations


class TelegramEngineError(RuntimeError):
    pass


class TelegramNotConfiguredError(TelegramEngineError):
    pass


class TelegramEntityNotFoundError(TelegramEngineError):
    pass

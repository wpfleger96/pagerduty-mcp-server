from typing import Any


class ApiRuntimeError(RuntimeError):
    """RuntimeError with an optional response payload for tests."""

    response: Any | None = None

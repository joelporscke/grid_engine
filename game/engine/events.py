from __future__ import annotations

from collections import defaultdict
from typing import Callable


class EventBus:
    """Simple pub/sub event bus. Systems communicate via events, not directly."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[[dict], None]]] = defaultdict(list)

    def on(self, event_name: str, callback: Callable[[dict], None]) -> None:
        self._listeners[event_name].append(callback)

    def emit(self, event_name: str, data: dict) -> None:
        for callback in self._listeners[event_name]:
            callback(data)

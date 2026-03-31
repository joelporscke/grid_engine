from __future__ import annotations


class TurnManager:
    """Tracks whose turn it is. Generic – no game-specific logic."""

    def __init__(self, player_ids: list[int]) -> None:
        self._player_ids: list[int] = player_ids
        self._current_index: int = 0

    @property
    def current_player(self) -> int:
        return self._player_ids[self._current_index]

    def advance(self) -> int:
        """Move to the next player. Returns the new current player id."""
        self._current_index = (self._current_index + 1) % len(self._player_ids)
        return self.current_player

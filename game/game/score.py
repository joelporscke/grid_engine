from __future__ import annotations

# Victory and scoring constants – defined as data, easy to adjust
WIN_SCORE: int = 15
SCORE_KILL_UNIT: int = 1
SCORE_KILL_HERO: int = 5
SCORE_DESTROY_BUILDING: int = 2
SCORE_DESTROY_BASE: int = 10


class ScoreManager:
    """Tracks score per player. Checks win condition."""

    def __init__(self) -> None:
        self._scores: dict[int, int] = {}

    def add_score(self, player_id: int, points: int) -> None:
        self._scores[player_id] = self._scores.get(player_id, 0) + points

    def get_score(self, player_id: int) -> int:
        return self._scores.get(player_id, 0)

    def get_winner(self) -> int | None:
        """Return player_id of the winner if win condition is met, else None."""
        for pid, score in self._scores.items():
            if score >= WIN_SCORE:
                return pid
        return None

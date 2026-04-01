"""Fog of War system.

Engine-level – no game-specific imports.
The caller (main.py / game code) computes unit positions and LoS values and
passes them as a plain list of (col, row, los) tuples.

Vision-blocking terrain can be SEEN (you see into it one tile) but stops
sight from propagating further.  This matches the design rule:
"Man ser en ruta in, aldrig igenom."
"""
from __future__ import annotations

from engine.grid import FogState, Grid


class FogSystem:
    """Manages per-player fog maps and applies them to the Grid.

    Separation:
    - update()       → recomputes visibility from supplied unit data
    - apply_to_grid() → writes current player's fog state into Cell.fog_state

    When fog_enabled is False, apply_to_grid marks all cells VISIBLE
    (useful for debugging).
    """

    def __init__(
        self,
        cols: int,
        rows: int,
        player_ids: list[int],
    ) -> None:
        self._cols: int = cols
        self._rows: int = rows
        self.fog_enabled: bool = True

        # All cells start UNKNOWN for every player
        self._fog: dict[int, list[list[FogState]]] = {
            pid: [[FogState.UNKNOWN] * cols for _ in range(rows)]
            for pid in player_ids
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def toggle(self) -> None:
        """Toggle fog of war on/off (debugging aid)."""
        self.fog_enabled = not self.fog_enabled

    def update(
        self,
        player_id: int,
        unit_positions: list[tuple[int, int, int]],  # (col, row, los)
        grid: Grid,
    ) -> None:
        """Recompute visibility for *player_id* given their units' positions.

        Args:
            unit_positions: list of (col, row, line_of_sight_range) for every
                            unit owned by this player that can see.
        """
        if not self.fog_enabled:
            return

        fog: list[list[FogState]] = self._fog[player_id]

        # Step 1 – transition all currently VISIBLE cells to SEEN
        for row in range(self._rows):
            for col in range(self._cols):
                if fog[row][col] == FogState.VISIBLE:
                    fog[row][col] = FogState.SEEN

        # Step 2 – mark cells visible from each unit
        for ucol, urow, los in unit_positions:
            for vcol, vrow in _compute_visible_cells(grid, ucol, urow, los):
                fog[vrow][vcol] = FogState.VISIBLE

    def apply_to_grid(self, player_id: int, grid: Grid) -> None:
        """Copy *player_id*'s fog map into Cell.fog_state on the grid."""
        if not self.fog_enabled:
            for row in range(self._rows):
                for col in range(self._cols):
                    grid.set_fog_state(col, row, FogState.VISIBLE)
            return

        fog: list[list[FogState]] = self._fog[player_id]
        for row in range(self._rows):
            for col in range(self._cols):
                grid.set_fog_state(col, row, fog[row][col])


# ---------------------------------------------------------------------------
# Module-level helpers (pure functions, only read Grid state)
# ---------------------------------------------------------------------------

def _compute_visible_cells(
    grid: Grid,
    unit_col: int,
    unit_row: int,
    los: int,
) -> set[tuple[int, int]]:
    """Return the set of (col, row) cells visible from *unit_col/row* within *los*.

    Uses Manhattan-distance range and ray-based line-of-sight checking.
    """
    visible: set[tuple[int, int]] = set()

    for tcol in range(unit_col - los, unit_col + los + 1):
        for trow in range(unit_row - los, unit_row + los + 1):
            if not grid.in_bounds(tcol, trow):
                continue
            if abs(tcol - unit_col) + abs(trow - unit_row) > los:
                continue  # Outside Manhattan range
            if _has_clear_line_of_sight(grid, unit_col, unit_row, tcol, trow):
                visible.add((tcol, trow))

    return visible


def _has_clear_line_of_sight(
    grid: Grid,
    from_col: int,
    from_row: int,
    to_col: int,
    to_row: int,
) -> bool:
    """Return True if *to_col/row* is visible from *from_col/row*.

    Vision-blocking cells ARE visible (you see INTO them) but stop the ray
    from going further.  Therefore only *intermediate* cells are checked for
    blocking; the target cell itself is always reachable if the path is clear.

    Uses linear interpolation (Chebyshev steps) for rasterisation.
    """
    dx: int = to_col - from_col
    dy: int = to_row - from_row
    steps: int = max(abs(dx), abs(dy))

    if steps == 0:
        return True

    for i in range(1, steps):
        t: float = i / steps
        col: int = int(from_col + dx * t + 0.5)
        row: int = int(from_row + dy * t + 0.5)
        if grid.in_bounds(col, row) and grid.get_cell(col, row).terrain_type.vision_blocking:
            return False   # Intermediate blocking cell – sight stops here

    return True  # Target cell is reachable (may itself be vision_blocking)

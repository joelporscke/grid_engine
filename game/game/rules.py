"""Map terrain definitions and procedural map creation for the 50×50 grid.

Terrain types are data – game rules always read properties (passable,
vision_blocking), never terrain names.

Map layout (both sides symmetric):
  - THICK_WOOD clusters near each base (flanks, north & south)
  - MOUNTAIN clusters slightly farther from base than thick wood
  - HUNTING_GROUNDS patches near the centre (risk/reward)
  - GRASS everywhere else (open corridors for movement)

Row 25 (vertical centre) is kept clear across the full width so armies can
meet after 5-10 turns of aggressive play.
"""
from __future__ import annotations

from engine.grid import Grid, TerrainType

# ---------------------------------------------------------------------------
# Terrain type definitions
# ---------------------------------------------------------------------------

GRASS: TerrainType = TerrainType(
    name="grass",
    passable=True,
    vision_blocking=False,
    color=(80, 120, 55),
)
THICK_WOOD: TerrainType = TerrainType(
    name="thick_wood",
    passable=False,
    vision_blocking=True,
    color=(30, 65, 25),
)
MOUNTAIN: TerrainType = TerrainType(
    name="mountain",
    passable=False,
    vision_blocking=True,
    color=(110, 100, 90),
)
HUNTING_GROUNDS: TerrainType = TerrainType(
    name="hunting_grounds",
    passable=True,
    vision_blocking=False,
    color=(140, 175, 60),
)

# ---------------------------------------------------------------------------
# Map dimensions and base positions
# ---------------------------------------------------------------------------
MAP_COLS: int = 50
MAP_ROWS: int = 50

P1_BASE_COL: int = 3
P1_BASE_ROW: int = 25
P2_BASE_COL: int = 46
P2_BASE_ROW: int = 25

# Shrine positions (one per player, near their start area)
P1_SHRINE_COL: int = 5
P1_SHRINE_ROW: int = 22
P2_SHRINE_COL: int = 44
P2_SHRINE_ROW: int = 22

# ---------------------------------------------------------------------------
# Terrain patches: (col_start, col_end, row_start, row_end)
# All ranges inclusive.
# ---------------------------------------------------------------------------

# --- Player 1 side ---
_P1_THICK_WOOD: list[tuple[int, int, int, int]] = [
    (6, 10, 13, 18),   # North flank
    (6, 10, 32, 37),   # South flank
]
_P1_MOUNTAIN: list[tuple[int, int, int, int]] = [
    (14, 18, 17, 21),  # North, farther than wood
    (14, 18, 29, 33),  # South
]

# --- Player 2 side (mirror) ---
_P2_THICK_WOOD: list[tuple[int, int, int, int]] = [
    (39, 43, 13, 18),
    (39, 43, 32, 37),
]
_P2_MOUNTAIN: list[tuple[int, int, int, int]] = [
    (31, 35, 17, 21),
    (31, 35, 29, 33),
]

# --- Centre: Hunting Grounds (toward the middle, risk/reward) ---
_HUNTING_GROUNDS: list[tuple[int, int, int, int]] = [
    (20, 24, 10, 15),   # North-left quadrant
    (26, 30, 10, 15),   # North-right quadrant
    (20, 24, 35, 40),   # South-left quadrant
    (26, 30, 35, 40),   # South-right quadrant
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fill_rect(
    grid: Grid,
    col_start: int,
    col_end: int,
    row_start: int,
    row_end: int,
    terrain: TerrainType,
) -> None:
    """Fill a rectangular region with *terrain*, clamped to grid bounds."""
    for col in range(col_start, col_end + 1):
        for row in range(row_start, row_end + 1):
            if grid.in_bounds(col, row):
                grid.set_terrain(col, row, terrain)


# ---------------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------------

def create_map(cols: int, rows: int) -> Grid:
    """Create the 50×50 game map with all four terrain types."""
    grid: Grid = Grid(cols=cols, rows=rows, default_terrain=GRASS)

    for patch in _P1_THICK_WOOD:
        _fill_rect(grid, *patch, THICK_WOOD)
    for patch in _P1_MOUNTAIN:
        _fill_rect(grid, *patch, MOUNTAIN)

    for patch in _P2_THICK_WOOD:
        _fill_rect(grid, *patch, THICK_WOOD)
    for patch in _P2_MOUNTAIN:
        _fill_rect(grid, *patch, MOUNTAIN)

    for patch in _HUNTING_GROUNDS:
        _fill_rect(grid, *patch, HUNTING_GROUNDS)

    return grid

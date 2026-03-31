from engine.grid import Grid, TerrainType

# Terrain type definitions – all game rules read properties, never terrain names
GRASS: TerrainType = TerrainType(name="grass", passable=True, color=(80, 120, 55))
FOREST: TerrainType = TerrainType(name="forest", passable=False, color=(30, 65, 25))

# Forest cell positions (col, row) for the starting map
_FOREST_POSITIONS: list[tuple[int, int]] = [
    (2, 1), (3, 1), (4, 1),
    (2, 2), (3, 2), (4, 2),
    (10, 4), (11, 4), (12, 4),
    (10, 5), (11, 5), (12, 5),
    (10, 6), (11, 6),
    (7, 11), (8, 11), (9, 11),
    (7, 12), (8, 12),
    (15, 7), (16, 7),
    (15, 8), (16, 8), (17, 8),
    (15, 9), (16, 9),
    (1, 16), (2, 16),
    (1, 17), (2, 17), (3, 17),
    (17, 14), (18, 14),
    (18, 15), (19, 15),
]


def create_map(cols: int, rows: int) -> Grid:
    """Create the starting game map with a mix of GRASS and FOREST."""
    grid: Grid = Grid(cols=cols, rows=rows, default_terrain=GRASS)
    for col, row in _FOREST_POSITIONS:
        if grid.in_bounds(col, row):
            grid.set_terrain(col, row, FOREST)
    return grid

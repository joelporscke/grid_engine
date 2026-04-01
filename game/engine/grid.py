from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from engine.ecs import EntityId


# ---------------------------------------------------------------------------
# Fog of War state – lives here to avoid circular imports with engine/fog.py
# ---------------------------------------------------------------------------

class FogState(Enum):
    UNKNOWN = 0   # Never seen – rendered black
    SEEN = 1      # Previously seen – rendered darkened
    VISIBLE = 2   # Currently visible – rendered normally


# ---------------------------------------------------------------------------
# Terrain
# ---------------------------------------------------------------------------

@dataclass
class TerrainType:
    name: str
    passable: bool
    vision_blocking: bool
    color: tuple[int, int, int]


# ---------------------------------------------------------------------------
# Cell and Grid
# ---------------------------------------------------------------------------

@dataclass
class Cell:
    terrain_type: TerrainType
    entity_id: EntityId | None = None
    fog_state: FogState = FogState.UNKNOWN


class Grid:
    def __init__(self, cols: int, rows: int, default_terrain: TerrainType) -> None:
        self.cols: int = cols
        self.rows: int = rows
        self._cells: list[list[Cell]] = [
            [Cell(terrain_type=default_terrain) for _ in range(cols)]
            for _ in range(rows)
        ]

    def get_cell(self, col: int, row: int) -> Cell:
        return self._cells[row][col]

    def set_terrain(self, col: int, row: int, terrain: TerrainType) -> None:
        self._cells[row][col].terrain_type = terrain

    def place_entity(self, col: int, row: int, entity_id: EntityId) -> None:
        self._cells[row][col].entity_id = entity_id

    def remove_entity(self, col: int, row: int) -> None:
        self._cells[row][col].entity_id = None

    def set_fog_state(self, col: int, row: int, state: FogState) -> None:
        self._cells[row][col].fog_state = state

    def in_bounds(self, col: int, row: int) -> bool:
        return 0 <= col < self.cols and 0 <= row < self.rows

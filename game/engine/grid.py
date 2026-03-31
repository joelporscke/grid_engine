from __future__ import annotations

from dataclasses import dataclass

from engine.ecs import EntityId


@dataclass
class TerrainType:
    name: str
    passable: bool
    color: tuple[int, int, int]


@dataclass
class Cell:
    terrain_type: TerrainType
    entity_id: EntityId | None = None


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

    def in_bounds(self, col: int, row: int) -> bool:
        return 0 <= col < self.cols and 0 <= row < self.rows

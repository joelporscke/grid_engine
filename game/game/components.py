from dataclasses import dataclass


@dataclass
class Position:
    x: int
    y: int


@dataclass
class Movement:
    range: int
    energy: int
    max_energy: int
    has_moved: bool = False


@dataclass
class Renderable:
    color: tuple[int, int, int]


@dataclass
class Selected:
    """Marker component. Entity is currently selected by the player."""


@dataclass
class OwnedBy:
    player_id: int

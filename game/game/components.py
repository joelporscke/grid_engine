from dataclasses import dataclass, field
from enum import Enum


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


# --- Unit type ---

class UnitKind(Enum):
    MELEE = "melee"
    ARCHER = "archer"
    HERO = "hero"


@dataclass
class Unit:
    kind: UnitKind


# --- Combat ---

@dataclass
class Health:
    hp: int
    max_hp: int


@dataclass
class Combat:
    attack: int
    attack_range: int   # 1 = adjacent only, >1 = ranged
    has_attacked: bool = False


# --- Archer mode ---

class ArcherMode(Enum):
    MOVE_ONLY = "move_only"           # Full move, no attack
    SHOOT_AND_MOVE = "shoot_and_move" # Attack (reduced dmg), then 1 step
    SHOOT_AND_STAY = "shoot_and_stay" # No move, full damage attack


@dataclass
class ArcherState:
    mode: ArcherMode = ArcherMode.SHOOT_AND_STAY


# --- Vision ---

@dataclass
class Vision:
    """Line-of-sight range in cells used by the Fog of War system."""
    los: int


# --- Map entities ---

@dataclass
class Shrine:
    """Marks this entity as a shrine. Control mechanics in Etapp 3."""
    pass

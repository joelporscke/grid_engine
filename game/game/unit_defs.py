"""Unit stat constants and factory functions.

All numeric values are named constants – never hardcoded elsewhere.
Factory functions create fully-wired entities in World and Grid.
"""
from __future__ import annotations

from engine.ecs import EntityId, World
from engine.grid import Grid
from game.components import (
    ArcherState,
    Combat,
    Health,
    Movement,
    OwnedBy,
    Position,
    Renderable,
    Unit,
    UnitKind,
    Vision,
)

# ---------------------------------------------------------------------------
# Melee
# ---------------------------------------------------------------------------
MELEE_HP: int = 20
MELEE_ATTACK: int = 8
MELEE_ATTACK_RANGE: int = 1
MELEE_MOVE_ENERGY: int = 5

# ---------------------------------------------------------------------------
# Archer
# ---------------------------------------------------------------------------
ARCHER_HP: int = 15
ARCHER_ATTACK: int = 10        # Full damage (shoot and stay)
ARCHER_ATTACK_RANGE: int = 4
ARCHER_MOVE_ENERGY: int = 4
# Shoot-and-move reduces damage by this ratio
ARCHER_SHOOT_MOVE_DAMAGE_RATIO: float = 0.7

# ---------------------------------------------------------------------------
# Hero  (~2x melee as per BALANCE.md)
# ---------------------------------------------------------------------------
HERO_HP: int = 40
HERO_ATTACK: int = 16
HERO_ATTACK_RANGE: int = 1
HERO_MOVE_ENERGY: int = 5

# ---------------------------------------------------------------------------
# Line of sight (from BALANCE.md)
# ---------------------------------------------------------------------------
MELEE_LOS: int = 5
ARCHER_LOS: int = 6
HERO_LOS: int = 5

# ---------------------------------------------------------------------------
# Combat rules
# ---------------------------------------------------------------------------
OPPORTUNITY_ATTACK_MULTIPLIER: int = 2      # 2x damage on opportunity attack
RANGED_IN_MELEE_DAMAGE_RATIO: float = 0.5   # Ranged unit at distance 1 → half damage

# ---------------------------------------------------------------------------
# Colors per player per unit type
# ---------------------------------------------------------------------------
PLAYER_UNIT_COLORS: dict[int, dict[UnitKind, tuple[int, int, int]]] = {
    1: {
        UnitKind.MELEE:  (220, 80, 60),
        UnitKind.ARCHER: (220, 150, 60),
        UnitKind.HERO:   (240, 220, 30),
    },
    2: {
        UnitKind.MELEE:  (60, 130, 220),
        UnitKind.ARCHER: (60, 180, 220),
        UnitKind.HERO:   (130, 80, 220),
    },
}

# Single-letter labels drawn on entity sprites
UNIT_KIND_LABELS: dict[UnitKind, str] = {
    UnitKind.MELEE:  "M",
    UnitKind.ARCHER: "A",
    UnitKind.HERO:   "H",
}

# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------

def create_melee(
    world: World, grid: Grid, player_id: int, col: int, row: int,
) -> EntityId:
    eid: EntityId = world.create_entity()
    color = PLAYER_UNIT_COLORS[player_id][UnitKind.MELEE]
    world.add_component(eid, Position(x=col, y=row))
    world.add_component(eid, Movement(
        range=MELEE_MOVE_ENERGY,
        energy=MELEE_MOVE_ENERGY,
        max_energy=MELEE_MOVE_ENERGY,
    ))
    world.add_component(eid, Health(hp=MELEE_HP, max_hp=MELEE_HP))
    world.add_component(eid, Combat(attack=MELEE_ATTACK, attack_range=MELEE_ATTACK_RANGE))
    world.add_component(eid, Unit(kind=UnitKind.MELEE))
    world.add_component(eid, Vision(los=MELEE_LOS))
    world.add_component(eid, Renderable(color=color))
    world.add_component(eid, OwnedBy(player_id=player_id))
    grid.place_entity(col, row, eid)
    return eid


def create_archer(
    world: World, grid: Grid, player_id: int, col: int, row: int,
) -> EntityId:
    eid: EntityId = world.create_entity()
    color = PLAYER_UNIT_COLORS[player_id][UnitKind.ARCHER]
    world.add_component(eid, Position(x=col, y=row))
    world.add_component(eid, Movement(
        range=ARCHER_MOVE_ENERGY,
        energy=ARCHER_MOVE_ENERGY,
        max_energy=ARCHER_MOVE_ENERGY,
    ))
    world.add_component(eid, Health(hp=ARCHER_HP, max_hp=ARCHER_HP))
    world.add_component(eid, Combat(attack=ARCHER_ATTACK, attack_range=ARCHER_ATTACK_RANGE))
    world.add_component(eid, Unit(kind=UnitKind.ARCHER))
    world.add_component(eid, ArcherState())
    world.add_component(eid, Vision(los=ARCHER_LOS))
    world.add_component(eid, Renderable(color=color))
    world.add_component(eid, OwnedBy(player_id=player_id))
    grid.place_entity(col, row, eid)
    return eid


def create_hero(
    world: World, grid: Grid, player_id: int, col: int, row: int,
) -> EntityId:
    """Hero: ~2x melee stats, does not count against pop space (UnitKind.HERO)."""
    eid: EntityId = world.create_entity()
    color = PLAYER_UNIT_COLORS[player_id][UnitKind.HERO]
    world.add_component(eid, Position(x=col, y=row))
    world.add_component(eid, Movement(
        range=HERO_MOVE_ENERGY,
        energy=HERO_MOVE_ENERGY,
        max_energy=HERO_MOVE_ENERGY,
    ))
    world.add_component(eid, Health(hp=HERO_HP, max_hp=HERO_HP))
    world.add_component(eid, Combat(attack=HERO_ATTACK, attack_range=HERO_ATTACK_RANGE))
    world.add_component(eid, Unit(kind=UnitKind.HERO))
    world.add_component(eid, Vision(los=HERO_LOS))
    world.add_component(eid, Renderable(color=color))
    world.add_component(eid, OwnedBy(player_id=player_id))
    grid.place_entity(col, row, eid)
    return eid

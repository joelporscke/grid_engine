from dataclasses import dataclass

from engine.ecs import EntityId


@dataclass
class SelectAction:
    entity_id: EntityId


@dataclass
class MoveAction:
    entity_id: EntityId
    target: tuple[int, int]


@dataclass
class AttackAction:
    attacker_id: EntityId
    target_id: EntityId


@dataclass
class EndTurnAction:
    player_id: int


@dataclass
class CycleArcherModeAction:
    entity_id: EntityId

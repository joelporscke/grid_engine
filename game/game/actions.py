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
class EndTurnAction:
    player_id: int

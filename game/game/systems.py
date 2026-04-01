"""Game systems: movement, combat, turn management.

Systems operate on components and communicate via the EventBus.
They do not call each other directly – shared kill logic lives in the
module-level kill_unit() helper.
"""
from __future__ import annotations

from engine.ecs import EntityId, World
from engine.events import EventBus
from engine.grid import Grid
from engine.turn import TurnManager
from game.actions import (
    AttackAction,
    CycleArcherModeAction,
    EndTurnAction,
    MoveAction,
    SelectAction,
)
from game.components import (
    ArcherMode,
    ArcherState,
    Combat,
    Health,
    Movement,
    OwnedBy,
    Position,
    Selected,
    Unit,
    UnitKind,
)
from game.score import SCORE_KILL_HERO, SCORE_KILL_UNIT, ScoreManager
from game.unit_defs import (
    ARCHER_SHOOT_MOVE_DAMAGE_RATIO,
    OPPORTUNITY_ATTACK_MULTIPLIER,
    RANGED_IN_MELEE_DAMAGE_RATIO,
)

# Movement rules
MOVE_ENERGY_COST: int = 1


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------

def kill_unit(
    entity_id: EntityId,
    killer_player_id: int,
    world: World,
    grid: Grid,
    events: EventBus,
    score_manager: ScoreManager,
) -> None:
    """Remove a killed unit from world and grid, award score to killer."""
    pos: Position | None = world.get_component(entity_id, Position)
    if pos is not None:
        grid.remove_entity(pos.x, pos.y)

    unit: Unit | None = world.get_component(entity_id, Unit)
    if unit is not None and unit.kind == UnitKind.HERO:
        score_manager.add_score(killer_player_id, SCORE_KILL_HERO)
    else:
        score_manager.add_score(killer_player_id, SCORE_KILL_UNIT)

    events.emit("unit_killed", {
        "entity_id": entity_id,
        "killer_player_id": killer_player_id,
    })
    world.destroy_entity(entity_id)


# ---------------------------------------------------------------------------
# MovementSystem
# ---------------------------------------------------------------------------

class MovementSystem:
    """Handles entity selection, movement, opportunity attacks, and archer mode cycling.

    Opportunity attack: when a unit leaves a cell adjacent to an enemy with
    Combat, that enemy deals 2× its attack as a free reaction.
    """

    def __init__(
        self,
        world: World,
        grid: Grid,
        events: EventBus,
        turn_manager: TurnManager,
        score_manager: ScoreManager,
    ) -> None:
        self._world: World = world
        self._grid: Grid = grid
        self._events: EventBus = events
        self._turn_manager: TurnManager = turn_manager
        self._score_manager: ScoreManager = score_manager

    # ------------------------------------------------------------------
    # Public action handlers
    # ------------------------------------------------------------------

    def handle_select(self, action: SelectAction) -> None:
        for eid in list(self._world.get_all(Selected).keys()):
            self._world.remove_component(eid, Selected)
        self._world.add_component(action.entity_id, Selected())
        self._events.emit("entity_selected", {"entity_id": action.entity_id})

    def handle_move(self, action: MoveAction) -> None:
        pos: Position | None = self._world.get_component(action.entity_id, Position)
        movement: Movement | None = self._world.get_component(action.entity_id, Movement)
        if pos is None or movement is None:
            return

        owner: OwnedBy | None = self._world.get_component(action.entity_id, OwnedBy)
        if owner is None or owner.player_id != self._turn_manager.current_player:
            return

        if movement.energy < MOVE_ENERGY_COST:
            return

        target_col, target_row = action.target
        if not self._is_valid_move(pos.x, pos.y, target_col, target_row):
            return

        # Archer in SHOOT_AND_STAY mode cannot move after attacking
        if self._is_shoot_and_stay_locked(action.entity_id):
            return

        # Apply opportunity attacks BEFORE completing the move
        killed = self._apply_opportunity_attacks(action.entity_id, pos.x, pos.y)
        if killed:
            return  # Unit died; do not complete the move

        self._grid.remove_entity(pos.x, pos.y)
        pos.x = target_col
        pos.y = target_row
        self._grid.place_entity(target_col, target_row, action.entity_id)
        movement.energy -= MOVE_ENERGY_COST

        self._events.emit("entity_moved", {
            "entity_id": action.entity_id,
            "to": (target_col, target_row),
        })

    def handle_cycle_archer_mode(self, action: CycleArcherModeAction) -> None:
        unit: Unit | None = self._world.get_component(action.entity_id, Unit)
        if unit is None or unit.kind != UnitKind.ARCHER:
            return

        owner: OwnedBy | None = self._world.get_component(action.entity_id, OwnedBy)
        if owner is None or owner.player_id != self._turn_manager.current_player:
            return

        archer_state: ArcherState | None = self._world.get_component(action.entity_id, ArcherState)
        if archer_state is None:
            return

        modes: list[ArcherMode] = [
            ArcherMode.MOVE_ONLY,
            ArcherMode.SHOOT_AND_MOVE,
            ArcherMode.SHOOT_AND_STAY,
        ]
        current_index: int = modes.index(archer_state.mode)
        archer_state.mode = modes[(current_index + 1) % len(modes)]

        self._events.emit("archer_mode_changed", {
            "entity_id": action.entity_id,
            "mode": archer_state.mode,
        })

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_valid_move(
        self, from_col: int, from_row: int, to_col: int, to_row: int,
    ) -> bool:
        if abs(to_col - from_col) + abs(to_row - from_row) != 1:
            return False
        if not self._grid.in_bounds(to_col, to_row):
            return False
        target_cell = self._grid.get_cell(to_col, to_row)
        if not target_cell.terrain_type.passable:
            return False
        if target_cell.entity_id is not None:
            return False
        return True

    def _is_shoot_and_stay_locked(self, entity_id: EntityId) -> bool:
        """Returns True if this is an archer in SHOOT_AND_STAY that has already attacked."""
        combat: Combat | None = self._world.get_component(entity_id, Combat)
        if combat is None or not combat.has_attacked:
            return False
        archer_state: ArcherState | None = self._world.get_component(entity_id, ArcherState)
        return archer_state is not None and archer_state.mode == ArcherMode.SHOOT_AND_STAY

    def _apply_opportunity_attacks(
        self, entity_id: EntityId, col: int, row: int,
    ) -> bool:
        """Apply 2× damage from each adjacent enemy. Returns True if the entity was killed."""
        owner: OwnedBy | None = self._world.get_component(entity_id, OwnedBy)
        entity_health: Health | None = self._world.get_component(entity_id, Health)
        if owner is None or entity_health is None:
            return False

        killer_player_id: int | None = None

        for dcol, drow in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            adj_col = col + dcol
            adj_row = row + drow
            if not self._grid.in_bounds(adj_col, adj_row):
                continue
            adj_cell = self._grid.get_cell(adj_col, adj_row)
            if adj_cell.entity_id is None:
                continue
            adj_id: EntityId = adj_cell.entity_id
            adj_owner: OwnedBy | None = self._world.get_component(adj_id, OwnedBy)
            if adj_owner is None or adj_owner.player_id == owner.player_id:
                continue
            adj_combat: Combat | None = self._world.get_component(adj_id, Combat)
            if adj_combat is None:
                continue

            damage: int = adj_combat.attack * OPPORTUNITY_ATTACK_MULTIPLIER
            entity_health.hp -= damage
            killer_player_id = adj_owner.player_id
            self._events.emit("opportunity_attack", {
                "attacker_id": adj_id,
                "target_id": entity_id,
                "damage": damage,
            })

        if entity_health.hp <= 0:
            if killer_player_id is not None:
                kill_unit(
                    entity_id, killer_player_id,
                    self._world, self._grid, self._events, self._score_manager,
                )
            return True
        return False


# ---------------------------------------------------------------------------
# CombatSystem
# ---------------------------------------------------------------------------

class CombatSystem:
    """Handles AttackAction: validates, calculates damage, kills units, awards score."""

    def __init__(
        self,
        world: World,
        grid: Grid,
        events: EventBus,
        turn_manager: TurnManager,
        score_manager: ScoreManager,
    ) -> None:
        self._world: World = world
        self._grid: Grid = grid
        self._events: EventBus = events
        self._turn_manager: TurnManager = turn_manager
        self._score_manager: ScoreManager = score_manager

    def handle_attack(self, action: AttackAction) -> None:
        # --- Validate attacker ---
        attacker_owner: OwnedBy | None = self._world.get_component(action.attacker_id, OwnedBy)
        if attacker_owner is None or attacker_owner.player_id != self._turn_manager.current_player:
            return

        attacker_combat: Combat | None = self._world.get_component(action.attacker_id, Combat)
        if attacker_combat is None or attacker_combat.has_attacked:
            return

        attacker_unit: Unit | None = self._world.get_component(action.attacker_id, Unit)

        # Archer in MOVE_ONLY mode cannot attack
        if attacker_unit is not None and attacker_unit.kind == UnitKind.ARCHER:
            archer_state: ArcherState | None = self._world.get_component(action.attacker_id, ArcherState)
            if archer_state is not None and archer_state.mode == ArcherMode.MOVE_ONLY:
                return

        # --- Validate target ---
        target_health: Health | None = self._world.get_component(action.target_id, Health)
        if target_health is None:
            return

        target_owner: OwnedBy | None = self._world.get_component(action.target_id, OwnedBy)
        if target_owner is None or target_owner.player_id == self._turn_manager.current_player:
            return

        # --- Check range ---
        attacker_pos: Position | None = self._world.get_component(action.attacker_id, Position)
        target_pos: Position | None = self._world.get_component(action.target_id, Position)
        if attacker_pos is None or target_pos is None:
            return

        distance: int = (
            abs(attacker_pos.x - target_pos.x) + abs(attacker_pos.y - target_pos.y)
        )
        if distance > attacker_combat.attack_range:
            return

        # --- Calculate damage ---
        damage: int = attacker_combat.attack

        # Ranged unit attacking at adjacent distance → half damage
        if attacker_combat.attack_range > 1 and distance == 1:
            damage = max(1, int(damage * RANGED_IN_MELEE_DAMAGE_RATIO))

        # Archer shoot-and-move → reduced damage
        if attacker_unit is not None and attacker_unit.kind == UnitKind.ARCHER:
            archer_state = self._world.get_component(action.attacker_id, ArcherState)
            if archer_state is not None and archer_state.mode == ArcherMode.SHOOT_AND_MOVE:
                damage = max(1, int(damage * ARCHER_SHOOT_MOVE_DAMAGE_RATIO))

        # --- Apply damage ---
        target_health.hp -= damage
        attacker_combat.has_attacked = True

        # --- Apply archer movement constraints after attack ---
        attacker_movement: Movement | None = self._world.get_component(action.attacker_id, Movement)
        if attacker_unit is not None and attacker_unit.kind == UnitKind.ARCHER and attacker_movement is not None:
            archer_state = self._world.get_component(action.attacker_id, ArcherState)
            if archer_state is not None:
                if archer_state.mode == ArcherMode.SHOOT_AND_STAY:
                    attacker_movement.energy = 0
                elif archer_state.mode == ArcherMode.SHOOT_AND_MOVE:
                    attacker_movement.energy = min(attacker_movement.energy, 1)

        self._events.emit("unit_attacked", {
            "attacker_id": action.attacker_id,
            "target_id": action.target_id,
            "damage": damage,
        })

        # --- Handle death ---
        if target_health.hp <= 0:
            kill_unit(
                action.target_id, attacker_owner.player_id,
                self._world, self._grid, self._events, self._score_manager,
            )


# ---------------------------------------------------------------------------
# TurnSystem
# ---------------------------------------------------------------------------

class TurnSystem:
    """End-of-turn: advances turn and resets next player's units."""

    def __init__(
        self, turn_manager: TurnManager, world: World, events: EventBus,
    ) -> None:
        self._turn_manager: TurnManager = turn_manager
        self._world: World = world
        self._events: EventBus = events

    def handle_end_turn(self, action: EndTurnAction) -> None:
        if action.player_id != self._turn_manager.current_player:
            return

        # Clear selection
        for eid in list(self._world.get_all(Selected).keys()):
            self._world.remove_component(eid, Selected)

        new_player: int = self._turn_manager.advance()

        # Restore movement energy and reset combat/archer state for new player
        for eid, movement in self._world.get_all(Movement).items():
            owner: OwnedBy | None = self._world.get_component(eid, OwnedBy)
            if owner is not None and owner.player_id == new_player:
                movement.energy = movement.max_energy
                movement.has_moved = False

        for eid, combat in self._world.get_all(Combat).items():
            owner = self._world.get_component(eid, OwnedBy)
            if owner is not None and owner.player_id == new_player:
                combat.has_attacked = False

        for eid, archer_state in self._world.get_all(ArcherState).items():
            owner = self._world.get_component(eid, OwnedBy)
            if owner is not None and owner.player_id == new_player:
                archer_state.mode = ArcherMode.SHOOT_AND_STAY

        self._events.emit("turn_ended", {"new_player": new_player})

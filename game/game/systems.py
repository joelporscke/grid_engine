from __future__ import annotations

from engine.ecs import World, EntityId
from engine.events import EventBus
from engine.grid import Grid
from engine.input import CellClick
from engine.turn import TurnManager
from game.actions import SelectAction, MoveAction, EndTurnAction
from game.components import Position, Movement, OwnedBy, Selected

# Movement rules – defined as data, not hardcoded in logic
MOVE_ENERGY_COST: int = 1


class MovementSystem:
    """Handles entity selection and movement.

    Only allows selecting and moving entities owned by the current player.
    Validates moves against terrain passability, grid bounds, and energy.
    """

    def __init__(
        self,
        world: World,
        grid: Grid,
        events: EventBus,
        turn_manager: TurnManager,
    ) -> None:
        self._world: World = world
        self._grid: Grid = grid
        self._events: EventBus = events
        self._turn_manager: TurnManager = turn_manager

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_click(self, click: CellClick) -> None:
        """Translate a cell click into an action and handle it."""
        if not self._grid.in_bounds(click.col, click.row):
            return

        clicked_entity: EntityId | None = self._grid.get_cell(click.col, click.row).entity_id
        selected_entity: EntityId | None = self._get_selected_entity()

        if clicked_entity is not None:
            owner = self._world.get_component(clicked_entity, OwnedBy)
            if owner is not None and owner.player_id == self._turn_manager.current_player:
                self._handle_select(SelectAction(entity_id=clicked_entity))
        elif selected_entity is not None:
            self._handle_move(MoveAction(
                entity_id=selected_entity,
                target=(click.col, click.row),
            ))

    # ------------------------------------------------------------------
    # Action handlers
    # ------------------------------------------------------------------

    def _handle_select(self, action: SelectAction) -> None:
        for eid in list(self._world.get_all(Selected).keys()):
            self._world.remove_component(eid, Selected)
        self._world.add_component(action.entity_id, Selected())
        self._events.emit("entity_selected", {"entity_id": action.entity_id})

    def _handle_move(self, action: MoveAction) -> None:
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

        self._grid.remove_entity(pos.x, pos.y)
        pos.x = target_col
        pos.y = target_row
        self._grid.place_entity(target_col, target_row, action.entity_id)
        movement.energy -= MOVE_ENERGY_COST

        self._events.emit("entity_moved", {
            "entity_id": action.entity_id,
            "to": (target_col, target_row),
        })

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_selected_entity(self) -> EntityId | None:
        selected = self._world.get_all(Selected)
        if selected:
            return next(iter(selected))
        return None

    def _is_valid_move(
        self,
        from_col: int,
        from_row: int,
        to_col: int,
        to_row: int,
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


class TurnSystem:
    """Handles end-of-turn logic: advances turn and restores next player's energy."""

    def __init__(self, turn_manager: TurnManager, world: World, events: EventBus) -> None:
        self._turn_manager: TurnManager = turn_manager
        self._world: World = world
        self._events: EventBus = events

    def handle_end_turn(self, action: EndTurnAction) -> None:
        if action.player_id != self._turn_manager.current_player:
            return

        for eid in list(self._world.get_all(Selected).keys()):
            self._world.remove_component(eid, Selected)

        new_player: int = self._turn_manager.advance()

        for eid, movement in self._world.get_all(Movement).items():
            owner: OwnedBy | None = self._world.get_component(eid, OwnedBy)
            if owner is not None and owner.player_id == new_player:
                movement.energy = movement.max_energy
                movement.has_moved = False

        self._events.emit("turn_ended", {"new_player": new_player})

"""Entry point for Grid Engine.

Wires together: ECS world, grid, systems, and the render loop.
Input routing lives here – systems expose public action handlers and
do not call each other.
"""
import sys

import pygame

from engine.ecs import EntityId, World
from engine.events import EventBus
from engine.fog import FogSystem
from engine.grid import FogState, Grid
from engine.input import cell_click_from_event
from engine.renderer import (
    CELL_HEIGHT,
    CELL_WIDTH,
    END_TURN_BUTTON_H,
    END_TURN_BUTTON_W,
    END_TURN_BUTTON_X,
    END_TURN_BUTTON_Y,
    GRID_COLS,
    GRID_HEIGHT,
    GRID_ROWS,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
    EntitySprite,
    UIState,
    render_frame,
)
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
    Renderable,
    Selected,
    Shrine,
    Unit,
    UnitKind,
    Vision,
)
from game.rules import (
    P1_SHRINE_COL,
    P1_SHRINE_ROW,
    P2_SHRINE_COL,
    P2_SHRINE_ROW,
    create_map,
)
from game.score import ScoreManager
from game.systems import CombatSystem, MovementSystem, TurnSystem
from game.unit_defs import (
    UNIT_KIND_LABELS,
    create_archer,
    create_hero,
    create_melee,
)

# ---------------------------------------------------------------------------
# Game constants
# ---------------------------------------------------------------------------
TARGET_FPS: int = 60

PLAYER_1_ID: int = 1
PLAYER_2_ID: int = 2

# Player UI colors (also used for the "Spelare X" label)
PLAYER_UI_COLORS: dict[int, tuple[int, int, int]] = {
    PLAYER_1_ID: (220, 80, 60),
    PLAYER_2_ID: (60, 130, 220),
}

# Starting positions for 50×50 map – bases at col 3 and col 46, row 25
P1_HERO_COL: int = 3
P1_HERO_ROW: int = 25
P1_MELEE_COL: int = 3
P1_MELEE_ROW: int = 23
P1_ARCHER_COL: int = 3
P1_ARCHER_ROW: int = 27

P2_HERO_COL: int = 46
P2_HERO_ROW: int = 25
P2_MELEE_COL: int = 46
P2_MELEE_ROW: int = 23
P2_ARCHER_COL: int = 46
P2_ARCHER_ROW: int = 27

# Shrine rendering color
COLOR_SHRINE: tuple[int, int, int] = (200, 160, 50)

# Human-readable unit kind names shown in UI
UNIT_KIND_NAMES: dict[UnitKind, str] = {
    UnitKind.MELEE:  "Melee",
    UnitKind.ARCHER: "Archer",
    UnitKind.HERO:   "Hero",
}

# Human-readable archer mode names
ARCHER_MODE_DISPLAY: dict[ArcherMode, str] = {
    ArcherMode.MOVE_ONLY:      "Rör dig",
    ArcherMode.SHOOT_AND_MOVE: "Skjut+rörelse",
    ArcherMode.SHOOT_AND_STAY: "Skjut+stanna",
}


# ---------------------------------------------------------------------------
# Input routing
# ---------------------------------------------------------------------------

def _get_selected_entity(world: World) -> EntityId | None:
    selected = world.get_all(Selected)
    return next(iter(selected), None) if selected else None


def handle_click(
    col: int,
    row: int,
    world: World,
    grid: Grid,
    turn_manager: TurnManager,
    movement_system: MovementSystem,
    combat_system: CombatSystem,
) -> None:
    """Route a grid cell click to the correct system action."""
    if not grid.in_bounds(col, row):
        return

    clicked_entity: EntityId | None = grid.get_cell(col, row).entity_id
    selected_entity: EntityId | None = _get_selected_entity(world)
    current_player: int = turn_manager.current_player

    if clicked_entity is not None:
        clicked_owner: OwnedBy | None = world.get_component(clicked_entity, OwnedBy)
        if clicked_owner is not None and clicked_owner.player_id == current_player:
            # Click on own unit → select it
            movement_system.handle_select(SelectAction(entity_id=clicked_entity))
        elif (
            selected_entity is not None
            and clicked_owner is not None
            and clicked_owner.player_id != current_player
        ):
            # Click on enemy with own unit selected → attack
            combat_system.handle_attack(AttackAction(
                attacker_id=selected_entity,
                target_id=clicked_entity,
            ))
    elif selected_entity is not None:
        # Click on empty cell with own unit selected → move
        movement_system.handle_move(MoveAction(
            entity_id=selected_entity,
            target=(col, row),
        ))


# ---------------------------------------------------------------------------
# Fog helpers
# ---------------------------------------------------------------------------

def _get_unit_los_data(
    world: World,
    player_id: int,
) -> list[tuple[int, int, int]]:
    """Return (col, row, los) for every unit owned by *player_id* that has Vision."""
    result: list[tuple[int, int, int]] = []
    for entity_id, owned in world.get_all(OwnedBy).items():
        if owned.player_id != player_id:
            continue
        pos: Position | None = world.get_component(entity_id, Position)
        vision: Vision | None = world.get_component(entity_id, Vision)
        if pos is not None and vision is not None:
            result.append((pos.x, pos.y, vision.los))
    return result


# ---------------------------------------------------------------------------
# Frame data builders
# ---------------------------------------------------------------------------

def build_sprites(world: World, grid: Grid) -> list[EntitySprite]:
    """Collect rendering data for all entities that are currently VISIBLE."""
    sprites: list[EntitySprite] = []
    for entity_id, pos in world.get_all(Position).items():
        renderable: Renderable | None = world.get_component(entity_id, Renderable)
        if renderable is None:
            continue

        # Skip entities in non-visible cells
        if grid.in_bounds(pos.x, pos.y):
            if grid.get_cell(pos.x, pos.y).fog_state != FogState.VISIBLE:
                continue

        is_selected: bool = world.get_component(entity_id, Selected) is not None

        unit: Unit | None = world.get_component(entity_id, Unit)
        label: str = UNIT_KIND_LABELS.get(unit.kind, "") if unit else ""

        health: Health | None = world.get_component(entity_id, Health)
        hp_ratio: float = (health.hp / health.max_hp) if health else 1.0

        combat: Combat | None = world.get_component(entity_id, Combat)
        has_attacked: bool = combat.has_attacked if combat else False

        sprites.append(EntitySprite(
            col=pos.x,
            row=pos.y,
            color=renderable.color,
            selected=is_selected,
            label=label,
            hp_ratio=hp_ratio,
            has_attacked=has_attacked,
        ))
    return sprites


def build_ui_state(
    world: World,
    turn_manager: TurnManager,
    score_manager: ScoreManager,
    fog_system: FogSystem,
) -> UIState:
    """Build UI rendering data from selected entity and score state."""
    current_player: int = turn_manager.current_player
    player_color: tuple[int, int, int] = PLAYER_UI_COLORS.get(
        current_player, (180, 180, 180),
    )

    energy: int = 0
    max_energy: int = 0
    selected_label: str = ""
    selected_hp_str: str = ""
    selected_can_attack: bool = False
    selected_archer_mode: str = ""

    selected_id: EntityId | None = _get_selected_entity(world)
    if selected_id is not None:
        mv: Movement | None = world.get_component(selected_id, Movement)
        if mv is not None:
            energy = mv.energy
            max_energy = mv.max_energy

        unit: Unit | None = world.get_component(selected_id, Unit)
        if unit is not None:
            selected_label = UNIT_KIND_NAMES.get(unit.kind, "")

        health: Health | None = world.get_component(selected_id, Health)
        if health is not None:
            selected_hp_str = f"{health.hp}/{health.max_hp}"

        combat: Combat | None = world.get_component(selected_id, Combat)
        if combat is not None:
            selected_can_attack = not combat.has_attacked

        if unit is not None and unit.kind == UnitKind.ARCHER:
            archer_state: ArcherState | None = world.get_component(selected_id, ArcherState)
            if archer_state is not None:
                selected_archer_mode = ARCHER_MODE_DISPLAY.get(archer_state.mode, "")

    return UIState(
        active_player=current_player,
        player_color=player_color,
        energy=energy,
        max_energy=max_energy,
        score_p1=score_manager.get_score(PLAYER_1_ID),
        score_p2=score_manager.get_score(PLAYER_2_ID),
        selected_label=selected_label,
        selected_hp_str=selected_hp_str,
        selected_can_attack=selected_can_attack,
        selected_archer_mode=selected_archer_mode,
        fog_enabled=fog_system.fog_enabled,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock: pygame.time.Clock = pygame.time.Clock()

    # Core engine objects
    grid: Grid = create_map(cols=GRID_COLS, rows=GRID_ROWS)
    events: EventBus = EventBus()
    world: World = World()
    score_manager: ScoreManager = ScoreManager()
    turn_manager: TurnManager = TurnManager(player_ids=[PLAYER_1_ID, PLAYER_2_ID])
    fog_system: FogSystem = FogSystem(
        cols=GRID_COLS, rows=GRID_ROWS,
        player_ids=[PLAYER_1_ID, PLAYER_2_ID],
    )

    # --- Create units for Player 1 ---
    create_hero(world, grid,   PLAYER_1_ID, P1_HERO_COL,   P1_HERO_ROW)
    create_melee(world, grid,  PLAYER_1_ID, P1_MELEE_COL,  P1_MELEE_ROW)
    create_archer(world, grid, PLAYER_1_ID, P1_ARCHER_COL, P1_ARCHER_ROW)

    # --- Create units for Player 2 ---
    create_hero(world, grid,   PLAYER_2_ID, P2_HERO_COL,   P2_HERO_ROW)
    create_melee(world, grid,  PLAYER_2_ID, P2_MELEE_COL,  P2_MELEE_ROW)
    create_archer(world, grid, PLAYER_2_ID, P2_ARCHER_COL, P2_ARCHER_ROW)

    # --- Create shrines (no grid.place_entity – they don't block movement) ---
    shrine_p1: EntityId = world.create_entity()
    world.add_component(shrine_p1, Position(x=P1_SHRINE_COL, y=P1_SHRINE_ROW))
    world.add_component(shrine_p1, Renderable(color=COLOR_SHRINE))
    world.add_component(shrine_p1, Shrine())

    shrine_p2: EntityId = world.create_entity()
    world.add_component(shrine_p2, Position(x=P2_SHRINE_COL, y=P2_SHRINE_ROW))
    world.add_component(shrine_p2, Renderable(color=COLOR_SHRINE))
    world.add_component(shrine_p2, Shrine())

    # --- Systems ---
    movement_system: MovementSystem = MovementSystem(
        world=world, grid=grid, events=events,
        turn_manager=turn_manager, score_manager=score_manager,
    )
    combat_system: CombatSystem = CombatSystem(
        world=world, grid=grid, events=events,
        turn_manager=turn_manager, score_manager=score_manager,
    )
    turn_system: TurnSystem = TurnSystem(
        turn_manager=turn_manager, world=world, events=events,
    )

    # End Turn button rect (for hit-testing)
    end_turn_btn: pygame.Rect = pygame.Rect(
        END_TURN_BUTTON_X, END_TURN_BUTTON_Y,
        END_TURN_BUTTON_W, END_TURN_BUTTON_H,
    )

    # ---------------------------------------------------------------------------
    # Game loop
    # ---------------------------------------------------------------------------
    running: bool = True
    while running:
        winner_id: int | None = score_manager.get_winner()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f:
                    fog_system.toggle()
                elif event.key == pygame.K_m and winner_id is None:
                    # Cycle archer mode for selected unit
                    sel = _get_selected_entity(world)
                    if sel is not None:
                        movement_system.handle_cycle_archer_mode(
                            CycleArcherModeAction(entity_id=sel)
                        )

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if winner_id is not None:
                    continue  # Game over – ignore clicks

                if end_turn_btn.collidepoint(event.pos):
                    turn_system.handle_end_turn(
                        EndTurnAction(player_id=turn_manager.current_player)
                    )
                elif event.pos[1] < GRID_HEIGHT:
                    col: int = event.pos[0] // CELL_WIDTH
                    row: int = event.pos[1] // CELL_HEIGHT
                    handle_click(
                        col, row,
                        world, grid, turn_manager,
                        movement_system, combat_system,
                    )

        # Update fog for current player, then apply to grid
        current_player: int = turn_manager.current_player
        unit_los_data = _get_unit_los_data(world, current_player)
        fog_system.update(current_player, unit_los_data, grid)
        fog_system.apply_to_grid(current_player, grid)

        # Render
        sprites: list[EntitySprite] = build_sprites(world, grid)
        ui_state: UIState = build_ui_state(world, turn_manager, score_manager, fog_system)
        winner_color = PLAYER_UI_COLORS.get(winner_id) if winner_id else None
        render_frame(screen, grid, sprites, ui_state, winner_id, winner_color)
        pygame.display.flip()
        clock.tick(TARGET_FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

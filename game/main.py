import sys
import pygame

from engine.ecs import World, EntityId
from engine.events import EventBus
from engine.grid import Grid
from engine.input import cell_click_from_event
from engine.renderer import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    GRID_COLS,
    GRID_ROWS,
    GRID_HEIGHT,
    CELL_WIDTH,
    CELL_HEIGHT,
    END_TURN_BUTTON_X,
    END_TURN_BUTTON_Y,
    END_TURN_BUTTON_W,
    END_TURN_BUTTON_H,
    COLOR_UI_TEXT,
    EntitySprite,
    UIState,
    render_frame,
)
from engine.turn import TurnManager
from game.actions import EndTurnAction
from game.components import Position, Movement, Renderable, Selected, OwnedBy
from game.rules import create_map
from game.systems import MovementSystem, TurnSystem

# Game loop constants
TARGET_FPS: int = 60

# Player IDs
PLAYER_1_ID: int = 1
PLAYER_2_ID: int = 2

# Starting positions
P1_START_COL: int = 5
P1_START_ROW: int = 5
P2_START_COL: int = 14
P2_START_ROW: int = 14

# Movement stats (same for both players)
MOVEMENT_RANGE: int = 3
MOVEMENT_ENERGY: int = 3
MOVEMENT_MAX_ENERGY: int = 3

# Piece colors
COLOR_PIECE_PLAYER1: tuple[int, int, int] = (220, 80, 60)
COLOR_PIECE_PLAYER2: tuple[int, int, int] = (60, 130, 220)


def build_sprites(world: World) -> list[EntitySprite]:
    """Collect rendering data for all entities that have Position and Renderable."""
    sprites: list[EntitySprite] = []
    positions: dict[EntityId, Position] = world.get_all(Position)
    for entity_id, pos in positions.items():
        renderable: Renderable | None = world.get_component(entity_id, Renderable)
        if renderable is None:
            continue
        is_selected: bool = world.get_component(entity_id, Selected) is not None
        sprites.append(EntitySprite(
            col=pos.x,
            row=pos.y,
            color=renderable.color,
            selected=is_selected,
        ))
    return sprites


def build_ui_state(world: World, turn_manager: TurnManager) -> UIState:
    """Build UI rendering data from current player's entity state."""
    current_player: int = turn_manager.current_player
    energy: int = 0
    max_energy: int = 0
    player_color: tuple[int, int, int] = COLOR_UI_TEXT

    for eid, movement in world.get_all(Movement).items():
        owner: OwnedBy | None = world.get_component(eid, OwnedBy)
        if owner is not None and owner.player_id == current_player:
            energy = movement.energy
            max_energy = movement.max_energy
            renderable: Renderable | None = world.get_component(eid, Renderable)
            if renderable is not None:
                player_color = renderable.color
            break

    return UIState(
        active_player=current_player,
        player_color=player_color,
        energy=energy,
        max_energy=max_energy,
    )


def main() -> None:
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock: pygame.time.Clock = pygame.time.Clock()

    grid: Grid = create_map(cols=GRID_COLS, rows=GRID_ROWS)
    events: EventBus = EventBus()
    world: World = World()

    piece1: EntityId = world.create_entity()
    world.add_component(piece1, Position(x=P1_START_COL, y=P1_START_ROW))
    world.add_component(piece1, Movement(
        range=MOVEMENT_RANGE,
        energy=MOVEMENT_ENERGY,
        max_energy=MOVEMENT_MAX_ENERGY,
    ))
    world.add_component(piece1, Renderable(color=COLOR_PIECE_PLAYER1))
    world.add_component(piece1, OwnedBy(player_id=PLAYER_1_ID))
    grid.place_entity(P1_START_COL, P1_START_ROW, piece1)

    piece2: EntityId = world.create_entity()
    world.add_component(piece2, Position(x=P2_START_COL, y=P2_START_ROW))
    world.add_component(piece2, Movement(
        range=MOVEMENT_RANGE,
        energy=MOVEMENT_ENERGY,
        max_energy=MOVEMENT_MAX_ENERGY,
    ))
    world.add_component(piece2, Renderable(color=COLOR_PIECE_PLAYER2))
    world.add_component(piece2, OwnedBy(player_id=PLAYER_2_ID))
    grid.place_entity(P2_START_COL, P2_START_ROW, piece2)

    turn_manager: TurnManager = TurnManager(player_ids=[PLAYER_1_ID, PLAYER_2_ID])

    movement_system: MovementSystem = MovementSystem(
        world=world, grid=grid, events=events, turn_manager=turn_manager,
    )
    turn_system: TurnSystem = TurnSystem(
        turn_manager=turn_manager, world=world, events=events,
    )

    end_turn_btn: pygame.Rect = pygame.Rect(
        END_TURN_BUTTON_X, END_TURN_BUTTON_Y,
        END_TURN_BUTTON_W, END_TURN_BUTTON_H,
    )

    running: bool = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if end_turn_btn.collidepoint(event.pos):
                    turn_system.handle_end_turn(
                        EndTurnAction(player_id=turn_manager.current_player)
                    )
                elif event.pos[1] < GRID_HEIGHT:
                    click = cell_click_from_event(event, CELL_WIDTH, CELL_HEIGHT)
                    if click is not None:
                        movement_system.process_click(click)

        sprites: list[EntitySprite] = build_sprites(world)
        ui_state: UIState = build_ui_state(world, turn_manager)
        render_frame(screen, grid, sprites, ui_state)
        pygame.display.flip()
        clock.tick(TARGET_FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

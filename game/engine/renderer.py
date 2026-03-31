from __future__ import annotations

from dataclasses import dataclass

import pygame

from engine.grid import Grid

# Grid constants
GRID_COLS: int = 20
GRID_ROWS: int = 20

# Cell size (square) – derived from a fixed grid width
GRID_AREA_WIDTH: int = 640
CELL_WIDTH: int = GRID_AREA_WIDTH // GRID_COLS   # 32
CELL_HEIGHT: int = CELL_WIDTH                    # square cells
GRID_HEIGHT: int = CELL_HEIGHT * GRID_ROWS       # 640

# UI panel below the grid
UI_PANEL_HEIGHT: int = 60

# Window
WINDOW_WIDTH: int = GRID_AREA_WIDTH
WINDOW_HEIGHT: int = GRID_HEIGHT + UI_PANEL_HEIGHT   # 700
WINDOW_TITLE: str = "Grid Engine"

# Grid colors
COLOR_BACKGROUND: tuple[int, int, int] = (30, 30, 30)
COLOR_CELL_BORDER: tuple[int, int, int] = (20, 20, 20)
COLOR_SELECTION: tuple[int, int, int] = (255, 220, 50)
BORDER_WIDTH: int = 1
SELECTION_BORDER_WIDTH: int = 2

# Entity rendering
ENTITY_PADDING: int = 4

# UI colors
COLOR_UI_BACKGROUND: tuple[int, int, int] = (18, 18, 24)
COLOR_UI_TEXT: tuple[int, int, int] = (180, 180, 180)
COLOR_BUTTON_NORMAL: tuple[int, int, int] = (55, 55, 80)
COLOR_BUTTON_TEXT: tuple[int, int, int] = (220, 220, 220)
COLOR_ENERGY_EMPTY: tuple[int, int, int] = (70, 70, 70)

# UI layout
UI_FONT_SIZE: int = 20
UI_TEXT_PADDING: int = 15
UI_ROW1_Y: int = GRID_HEIGHT + 10
UI_ROW2_Y: int = GRID_HEIGHT + 36

# Energy dots
ENERGY_DOT_RADIUS: int = 6
ENERGY_DOT_SPACING: int = 18   # center-to-center

# End Turn button
END_TURN_BUTTON_W: int = 120
END_TURN_BUTTON_H: int = 40
END_TURN_BUTTON_X: int = WINDOW_WIDTH - END_TURN_BUTTON_W - 10
END_TURN_BUTTON_Y: int = GRID_HEIGHT + (UI_PANEL_HEIGHT - END_TURN_BUTTON_H) // 2

# Module-level font – initialized lazily after pygame.init()
_font: pygame.font.Font | None = None


def _get_font() -> pygame.font.Font:
    global _font
    if _font is None:
        _font = pygame.font.Font(None, UI_FONT_SIZE)
    return _font


@dataclass
class EntitySprite:
    """Pure rendering data for one entity. No game logic."""
    col: int
    row: int
    color: tuple[int, int, int]
    selected: bool = False


@dataclass
class UIState:
    """Pure rendering data for the UI panel. No game logic."""
    active_player: int
    player_color: tuple[int, int, int]
    energy: int
    max_energy: int


def draw_grid(surface: pygame.Surface, grid: Grid) -> None:
    """Draw all cells, reading terrain color from grid data."""
    for row in range(grid.rows):
        for col in range(grid.cols):
            cell = grid.get_cell(col, row)
            x: int = col * CELL_WIDTH
            y: int = row * CELL_HEIGHT
            cell_rect: pygame.Rect = pygame.Rect(x, y, CELL_WIDTH, CELL_HEIGHT)
            pygame.draw.rect(surface, cell.terrain_type.color, cell_rect)
            pygame.draw.rect(surface, COLOR_CELL_BORDER, cell_rect, BORDER_WIDTH)


def draw_entities(surface: pygame.Surface, sprites: list[EntitySprite]) -> None:
    """Draw all entity sprites. Selected entities get a highlighted border."""
    for sprite in sprites:
        x: int = sprite.col * CELL_WIDTH + ENTITY_PADDING
        y: int = sprite.row * CELL_HEIGHT + ENTITY_PADDING
        w: int = CELL_WIDTH - ENTITY_PADDING * 2
        h: int = CELL_HEIGHT - ENTITY_PADDING * 2
        entity_rect: pygame.Rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, sprite.color, entity_rect)
        if sprite.selected:
            pygame.draw.rect(surface, COLOR_SELECTION, entity_rect, SELECTION_BORDER_WIDTH)


def draw_ui(surface: pygame.Surface, ui_state: UIState) -> None:
    """Draw the UI panel: player label, energy dots, and End Turn button."""
    font = _get_font()

    panel_rect: pygame.Rect = pygame.Rect(0, GRID_HEIGHT, WINDOW_WIDTH, UI_PANEL_HEIGHT)
    pygame.draw.rect(surface, COLOR_UI_BACKGROUND, panel_rect)

    # Player label
    label: str = f"Spelare {ui_state.active_player}"
    label_surf = font.render(label, True, ui_state.player_color)
    surface.blit(label_surf, (UI_TEXT_PADDING, UI_ROW1_Y))

    # Energy dots
    for i in range(ui_state.max_energy):
        cx: int = UI_TEXT_PADDING + ENERGY_DOT_RADIUS + i * ENERGY_DOT_SPACING
        cy: int = UI_ROW2_Y + ENERGY_DOT_RADIUS
        if i < ui_state.energy:
            pygame.draw.circle(surface, ui_state.player_color, (cx, cy), ENERGY_DOT_RADIUS)
        else:
            pygame.draw.circle(surface, COLOR_ENERGY_EMPTY, (cx, cy), ENERGY_DOT_RADIUS)

    # End Turn button
    btn_rect: pygame.Rect = pygame.Rect(
        END_TURN_BUTTON_X, END_TURN_BUTTON_Y,
        END_TURN_BUTTON_W, END_TURN_BUTTON_H,
    )
    pygame.draw.rect(surface, COLOR_BUTTON_NORMAL, btn_rect, border_radius=4)
    btn_text_surf = font.render("Avsluta tur", True, COLOR_BUTTON_TEXT)
    btn_text_x: int = END_TURN_BUTTON_X + (END_TURN_BUTTON_W - btn_text_surf.get_width()) // 2
    btn_text_y: int = END_TURN_BUTTON_Y + (END_TURN_BUTTON_H - btn_text_surf.get_height()) // 2
    surface.blit(btn_text_surf, (btn_text_x, btn_text_y))


def render_frame(
    surface: pygame.Surface,
    grid: Grid,
    sprites: list[EntitySprite],
    ui_state: UIState,
) -> None:
    """Render one complete frame from scratch."""
    surface.fill(COLOR_BACKGROUND)
    draw_grid(surface, grid)
    draw_entities(surface, sprites)
    draw_ui(surface, ui_state)

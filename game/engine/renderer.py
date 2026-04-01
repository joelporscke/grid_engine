"""Renderer – reads state and draws to screen. No game logic here."""
from __future__ import annotations

from dataclasses import dataclass

import pygame

from engine.grid import FogState, Grid

# ---------------------------------------------------------------------------
# Grid / cell constants
# ---------------------------------------------------------------------------
GRID_COLS: int = 50
GRID_ROWS: int = 50

CELL_SIZE: int = 16               # Pixels per cell (square)
CELL_WIDTH: int = CELL_SIZE
CELL_HEIGHT: int = CELL_SIZE
GRID_AREA_WIDTH: int = CELL_SIZE * GRID_COLS   # 800
GRID_HEIGHT: int = CELL_SIZE * GRID_ROWS        # 800

# ---------------------------------------------------------------------------
# UI panel (below the grid)
# ---------------------------------------------------------------------------
UI_PANEL_HEIGHT: int = 90

WINDOW_WIDTH: int = GRID_AREA_WIDTH
WINDOW_HEIGHT: int = GRID_HEIGHT + UI_PANEL_HEIGHT   # 890
WINDOW_TITLE: str = "Grid Engine"

# UI row y-positions
UI_ROW1_Y: int = GRID_HEIGHT + 8    # Player label + scores
UI_ROW2_Y: int = GRID_HEIGHT + 28   # Energy dots + unit type
UI_ROW3_Y: int = GRID_HEIGHT + 50   # HP + archer mode
UI_ROW4_Y: int = GRID_HEIGHT + 70   # Extra info

# ---------------------------------------------------------------------------
# Colors – grid and fog
# ---------------------------------------------------------------------------
COLOR_BACKGROUND: tuple[int, int, int] = (30, 30, 30)
COLOR_CELL_BORDER: tuple[int, int, int] = (20, 20, 20)
COLOR_SELECTION: tuple[int, int, int] = (255, 220, 50)
BORDER_WIDTH: int = 1
SELECTION_BORDER_WIDTH: int = 2

COLOR_FOG_UNKNOWN: tuple[int, int, int] = (0, 0, 0)     # Never-seen cells: black
FOG_SEEN_RATIO: float = 0.40                              # SEEN cells: 40% brightness

# ---------------------------------------------------------------------------
# Colors – entity
# ---------------------------------------------------------------------------
ENTITY_PADDING: int = 2   # Smaller padding for 16-px cells
COLOR_ENTITY_LABEL: tuple[int, int, int] = (255, 255, 255)
COLOR_HP_HIGH: tuple[int, int, int] = (80, 200, 80)
COLOR_HP_MID: tuple[int, int, int] = (220, 180, 50)
COLOR_HP_LOW: tuple[int, int, int] = (200, 60, 60)
COLOR_HP_BAR_BG: tuple[int, int, int] = (60, 20, 20)
COLOR_ATTACKED_OVERLAY_ALPHA: int = 80

# ---------------------------------------------------------------------------
# Colors – UI
# ---------------------------------------------------------------------------
COLOR_UI_BACKGROUND: tuple[int, int, int] = (18, 18, 24)
COLOR_UI_TEXT: tuple[int, int, int] = (180, 180, 180)
COLOR_BUTTON_NORMAL: tuple[int, int, int] = (55, 55, 80)
COLOR_BUTTON_TEXT: tuple[int, int, int] = (220, 220, 220)
COLOR_ENERGY_EMPTY: tuple[int, int, int] = (70, 70, 70)
COLOR_WIN_OVERLAY: tuple[int, int, int] = (0, 0, 0)
WIN_OVERLAY_ALPHA: int = 160

# ---------------------------------------------------------------------------
# UI layout
# ---------------------------------------------------------------------------
UI_FONT_SIZE: int = 20
UI_TEXT_PADDING: int = 15
ENTITY_LABEL_FONT_SIZE: int = 11   # Smaller for 16-px cells

# Energy dots
ENERGY_DOT_RADIUS: int = 5
ENERGY_DOT_SPACING: int = 16   # center-to-center

# End Turn button
END_TURN_BUTTON_W: int = 120
END_TURN_BUTTON_H: int = 40
END_TURN_BUTTON_X: int = WINDOW_WIDTH - END_TURN_BUTTON_W - 10
END_TURN_BUTTON_Y: int = GRID_HEIGHT + (UI_PANEL_HEIGHT - END_TURN_BUTTON_H) // 2

# ---------------------------------------------------------------------------
# Lazy-loaded fonts
# ---------------------------------------------------------------------------
_font: pygame.font.Font | None = None
_entity_font: pygame.font.Font | None = None
_win_font: pygame.font.Font | None = None


def _get_font() -> pygame.font.Font:
    global _font
    if _font is None:
        _font = pygame.font.Font(None, UI_FONT_SIZE)
    return _font


def _get_entity_font() -> pygame.font.Font:
    global _entity_font
    if _entity_font is None:
        _entity_font = pygame.font.Font(None, ENTITY_LABEL_FONT_SIZE)
    return _entity_font


def _get_win_font() -> pygame.font.Font:
    global _win_font
    if _win_font is None:
        _win_font = pygame.font.Font(None, 52)
    return _win_font


# ---------------------------------------------------------------------------
# Data structs passed to drawing functions
# ---------------------------------------------------------------------------

@dataclass
class EntitySprite:
    """Pure rendering data for one entity. No game logic."""
    col: int
    row: int
    color: tuple[int, int, int]
    selected: bool = False
    label: str = ""         # Unit type letter ("M", "A", "H", "S")
    hp_ratio: float = 1.0   # 0.0–1.0 for HP bar
    has_attacked: bool = False


@dataclass
class UIState:
    """Pure rendering data for the UI panel. No game logic."""
    active_player: int
    player_color: tuple[int, int, int]
    energy: int
    max_energy: int
    score_p1: int = 0
    score_p2: int = 0
    selected_label: str = ""
    selected_hp_str: str = ""
    selected_can_attack: bool = False
    selected_archer_mode: str = ""
    fog_enabled: bool = True   # Shown in UI as indicator


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def _hp_color(ratio: float) -> tuple[int, int, int]:
    if ratio > 0.6:
        return COLOR_HP_HIGH
    if ratio > 0.3:
        return COLOR_HP_MID
    return COLOR_HP_LOW


def _darken_color(
    color: tuple[int, int, int], ratio: float
) -> tuple[int, int, int]:
    """Return *color* multiplied by *ratio* (used for SEEN fog state)."""
    return (
        int(color[0] * ratio),
        int(color[1] * ratio),
        int(color[2] * ratio),
    )


def draw_grid(surface: pygame.Surface, grid: Grid) -> None:
    """Draw all cells, applying fog-of-war shading based on Cell.fog_state."""
    for row in range(grid.rows):
        for col in range(grid.cols):
            cell = grid.get_cell(col, row)
            x: int = col * CELL_WIDTH
            y: int = row * CELL_HEIGHT
            cell_rect: pygame.Rect = pygame.Rect(x, y, CELL_WIDTH, CELL_HEIGHT)

            match cell.fog_state:
                case FogState.UNKNOWN:
                    pygame.draw.rect(surface, COLOR_FOG_UNKNOWN, cell_rect)
                case FogState.SEEN:
                    seen_color = _darken_color(cell.terrain_type.color, FOG_SEEN_RATIO)
                    pygame.draw.rect(surface, seen_color, cell_rect)
                case FogState.VISIBLE:
                    pygame.draw.rect(surface, cell.terrain_type.color, cell_rect)

            pygame.draw.rect(surface, COLOR_CELL_BORDER, cell_rect, BORDER_WIDTH)


def draw_entities(surface: pygame.Surface, sprites: list[EntitySprite]) -> None:
    """Draw entity sprites. Only VISIBLE entities are in the sprite list."""
    entity_font = _get_entity_font()

    for sprite in sprites:
        x: int = sprite.col * CELL_WIDTH + ENTITY_PADDING
        y: int = sprite.row * CELL_HEIGHT + ENTITY_PADDING
        w: int = CELL_WIDTH - ENTITY_PADDING * 2
        h: int = CELL_HEIGHT - ENTITY_PADDING * 2
        entity_rect: pygame.Rect = pygame.Rect(x, y, w, h)

        pygame.draw.rect(surface, sprite.color, entity_rect)

        # HP bar – bottom 2 px (only when damaged)
        if sprite.hp_ratio < 1.0:
            bar_y: int = y + h - 2
            pygame.draw.rect(surface, COLOR_HP_BAR_BG, (x, bar_y, w, 2))
            fill_w: int = max(1, int(w * sprite.hp_ratio))
            pygame.draw.rect(surface, _hp_color(sprite.hp_ratio), (x, bar_y, fill_w, 2))

        # Unit/entity label
        if sprite.label:
            label_surf = entity_font.render(sprite.label, True, COLOR_ENTITY_LABEL)
            lx: int = x + (w - label_surf.get_width()) // 2
            ly: int = y + (h - label_surf.get_height()) // 2
            surface.blit(label_surf, (lx, ly))

        # Dim overlay when unit has already attacked
        if sprite.has_attacked:
            overlay = pygame.Surface((w, h))
            overlay.set_alpha(COLOR_ATTACKED_OVERLAY_ALPHA)
            overlay.fill((0, 0, 0))
            surface.blit(overlay, (x, y))

        # Selection border drawn last
        if sprite.selected:
            pygame.draw.rect(surface, COLOR_SELECTION, entity_rect, SELECTION_BORDER_WIDTH)


def draw_ui(surface: pygame.Surface, ui_state: UIState) -> None:
    """Draw the UI panel: player label, scores, energy, unit info, End Turn button."""
    font = _get_font()

    panel_rect: pygame.Rect = pygame.Rect(0, GRID_HEIGHT, WINDOW_WIDTH, UI_PANEL_HEIGHT)
    pygame.draw.rect(surface, COLOR_UI_BACKGROUND, panel_rect)

    # Row 1 – player label, scores, fog indicator
    label: str = f"Spelare {ui_state.active_player}"
    label_surf = font.render(label, True, ui_state.player_color)
    surface.blit(label_surf, (UI_TEXT_PADDING, UI_ROW1_Y))

    score_text: str = f"P1: {ui_state.score_p1}p   P2: {ui_state.score_p2}p"
    score_surf = font.render(score_text, True, COLOR_UI_TEXT)
    surface.blit(score_surf, (UI_TEXT_PADDING + 130, UI_ROW1_Y))

    fog_text: str = "Dimma: PÅ  [F]" if ui_state.fog_enabled else "Dimma: AV  [F]"
    fog_color: tuple[int, int, int] = (120, 160, 200) if ui_state.fog_enabled else (180, 100, 80)
    fog_surf = font.render(fog_text, True, fog_color)
    surface.blit(fog_surf, (UI_TEXT_PADDING + 320, UI_ROW1_Y))

    # Row 2 – energy dots + selected unit label
    for i in range(ui_state.max_energy):
        cx: int = UI_TEXT_PADDING + ENERGY_DOT_RADIUS + i * ENERGY_DOT_SPACING
        cy: int = UI_ROW2_Y + ENERGY_DOT_RADIUS
        color = ui_state.player_color if i < ui_state.energy else COLOR_ENERGY_EMPTY
        pygame.draw.circle(surface, color, (cx, cy), ENERGY_DOT_RADIUS)

    if ui_state.selected_label:
        unit_text: str = ui_state.selected_label
        if ui_state.selected_can_attack:
            unit_text += "  [kan attackera]"
        unit_surf = font.render(unit_text, True, COLOR_UI_TEXT)
        dot_area_w: int = ui_state.max_energy * ENERGY_DOT_SPACING + ENERGY_DOT_RADIUS
        surface.blit(unit_surf, (UI_TEXT_PADDING + dot_area_w + 8, UI_ROW2_Y))

    # Row 3 – HP + archer mode
    info_parts: list[str] = []
    if ui_state.selected_hp_str:
        info_parts.append(f"HP: {ui_state.selected_hp_str}")
    if ui_state.selected_archer_mode:
        info_parts.append(f"Läge: {ui_state.selected_archer_mode}  [M]")
    if info_parts:
        info_surf = font.render("   ".join(info_parts), True, COLOR_UI_TEXT)
        surface.blit(info_surf, (UI_TEXT_PADDING, UI_ROW3_Y))

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


def draw_win_screen(
    surface: pygame.Surface,
    winner_id: int,
    winner_color: tuple[int, int, int],
) -> None:
    """Draw a semi-transparent win overlay."""
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(WIN_OVERLAY_ALPHA)
    overlay.fill(COLOR_WIN_OVERLAY)
    surface.blit(overlay, (0, 0))

    win_font = _get_win_font()
    text_surf = win_font.render(f"Spelare {winner_id} vinner!", True, winner_color)
    tx: int = (WINDOW_WIDTH - text_surf.get_width()) // 2
    ty: int = (WINDOW_HEIGHT - text_surf.get_height()) // 2
    surface.blit(text_surf, (tx, ty))

    small_font = _get_font()
    sub_surf = small_font.render("Tryck ESC för att avsluta", True, COLOR_UI_TEXT)
    sx: int = (WINDOW_WIDTH - sub_surf.get_width()) // 2
    surface.blit(sub_surf, (sx, ty + 60))


def render_frame(
    surface: pygame.Surface,
    grid: Grid,
    sprites: list[EntitySprite],
    ui_state: UIState,
    winner_id: int | None = None,
    winner_color: tuple[int, int, int] | None = None,
) -> None:
    """Render one complete frame from scratch."""
    surface.fill(COLOR_BACKGROUND)
    draw_grid(surface, grid)
    draw_entities(surface, sprites)
    draw_ui(surface, ui_state)
    if winner_id is not None:
        draw_win_screen(surface, winner_id, winner_color or COLOR_UI_TEXT)

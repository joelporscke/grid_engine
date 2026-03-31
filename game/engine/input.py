from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class CellClick:
    """A left mouse click translated to grid cell coordinates."""
    col: int
    row: int


def cell_click_from_event(
    event: pygame.event.Event,
    cell_width: int,
    cell_height: int,
) -> CellClick | None:
    """Return a CellClick if event is a left mouse button press, else None."""
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        col: int = event.pos[0] // cell_width
        row: int = event.pos[1] // cell_height
        return CellClick(col=col, row=row)
    return None

from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING, Iterable, Tuple

import enums.color as color

if TYPE_CHECKING:
    from tcod.console import Console



def render_bar(
    console: Console, current_value: int, maximum_value: int, total_width: int, x,y
) -> None:
    
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=x, y=y, width=total_width, height=1, ch=1, bg=color.bar_empty)

    if bar_width > 0:
        console.draw_rect(
            x=x, y=y, width=bar_width, height=1, ch=1, bg=color.bar_filled
        )

    console.print(
        x=x+1, y=y, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text
    )



def render_dungeon_level(
    console: Console, dungeon_level: int, location: Tuple[int, int]
) -> None:
    """
    Render the level the player is currently on, at the given location.
    """
    x, y = location

    console.print(x=x, y=y, string=f"Dungeon level: {dungeon_level}")

def wrap(string: str, width: int) -> Iterable[str]:
    """Return a wrapped text message."""
    for line in string.splitlines():  # Handle newlines in messages.
        yield from textwrap.wrap(
            line, width, expand_tabs=True,
        )
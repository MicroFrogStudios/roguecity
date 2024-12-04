from __future__ import annotations
 

from typing import Callable, Optional, Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from actions import Action

from classes.entity import Entity
from components.interactable_component import Interactable

from enums.render_order import RenderOrder


class Prop(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        description: str = "<Missing Description>",
        icon : str = "assets\sprites\\red_egg.png",
        interactables : list[Interactable] = [],
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            fgColor=color,
            name=name,
            description=description,
            blocks_movement=False,
            render_order=RenderOrder.PROP,
            icon = icon,
            interactables = interactables
        )
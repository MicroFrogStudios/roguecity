from typing import Tuple
from classes.entity import Entity
from components.interactable_component import Consumable
from enums.render_order import RenderOrder


class Item(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        description: str = "<Missing Description>",
        consumable: Consumable = None,
        icon : str = "assets\sprites\\red_egg.png"
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            fgColor=color,
            name=name,
            description=description,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
            icon = icon
        )
        if consumable is not None:
            self.consumable = consumable
            self.consumable.parent = self
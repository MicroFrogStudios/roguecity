from typing import Tuple
from classes.entity import Entity
from components.consumable_component import Consumable
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
        consumable: Consumable,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            fgColor=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
        )

        self.consumable = consumable
        self.consumable.parent = self
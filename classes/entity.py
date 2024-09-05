from __future__ import annotations

import copy
import math
from typing import Optional, Tuple, TypeVar, TYPE_CHECKING, Union

from components.inventory_component import Inventory
from enums.render_order import RenderOrder

if TYPE_CHECKING:
    from map.game_map import GameMap

T = TypeVar("T", bound="Entity")

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    parent: Union[GameMap,Inventory]

    def __init__(
        self,
        parent: Optional[GameMap] = None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        fgColor: Tuple[int, int, int] = (255, 255, 255),
        bgColor = None,
        name: str = "<Unnamed>",
        description: str = "<description missing>",
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
        icon: str = "assets\sprites\\red_egg.png",
    ):
        self.x = x
        self.y = y
        self.char = char
        self.fgColor = fgColor
        self.bgColor = bgColor 
        self.name = name
        self.description = description
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        self.icon = icon
        if parent:
            # If parent isn't provided now then it will be set later.
            self.parent = parent
            parent.entities.add(self)

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        gamemap.entities.add(clone)
        return clone
    
    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        """Place this entity at a new location.  Handles moving across GameMaps."""
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "parent") and self.parent is self.gamemap:  # Possibly uninitialized.
                self.parent.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        """
        Return the distance between the current entity and the given (x, y) coordinate.
        """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy
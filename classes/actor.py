from __future__ import annotations

import copy
from enum import Enum
from classes.entity import Entity
from typing import Optional, Type, Tuple, TYPE_CHECKING
from enums.render_order import RenderOrder
import enums.color as ecolor
if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.fighter_component import Fighter

from components.inventory_component import Inventory, Equipment
    
from components.interactor_component import Interactor


class Actor(Entity):
        
    class Type(Enum):
        NPC = "NPC"
        PLAYER = "PLAYER"
        MONSTER = "MONSTER"
        CRITTER = "CRITTER"
            
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = ecolor.white,
        name: str = "<Unnamed>",
        description: str = "<Missing description>",
        friendly_ai: BaseAI = None,
        hostile_ai : BaseAI = None,
        fighter: Fighter,
        inventory: Inventory,
        hostile: bool,
        actor_type,
        icon: str = "assets\sprites\\red_egg.png",
        interactables = None

    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            fgColor=color,
            name=name,
            description=description,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
            icon=icon,
            interactables=interactables
        )
        
        if friendly_ai:
            friendly_ai.entity = self
            self.friendly_ai = friendly_ai
        if hostile_ai:
            hostile_ai.entity = self
            self.hostile_ai = hostile_ai
        self.fighter = fighter
        self.fighter.parent = self
        
        self.inventory = inventory
        self.inventory.parent = self

        self.equipment = Equipment()
        self.equipment.parent= self

        self.interactor = Interactor()
        self.interactor.parent = self
        
        self.hostile = hostile
        
        if self.hostile:
            self.ai = self.hostile_ai
        else:
            self.ai = self.friendly_ai
        self.actor_type = actor_type

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)
        
    def turn_hostile(self):
        self.hostile = True
        self.ai = self.hostile_ai
        
    def turn_friendly(self):
        self.hostile=False
        self.ai = self.friendly_ai
from __future__ import annotations
 

from enum import Enum
from typing import Callable, Optional, Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from actions import Action

from classes.entity import Entity
from components.interactable_component import EquipInteractable, PickUpInteractable,DropInteractable, Interactable, UnequipInteractable
from components.inventory_component import Equipment, Inventory
from enums.render_order import RenderOrder


class Item(Entity):

    class Type(Enum):
        FOOD = "FOOD"
        SCROLL = "SCROLL"
        EQUIP = "EQUIP"
        KEY = "KEY"
        OTHER = "OTHER"

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
        item_type: Item.Type = Type.OTHER
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
            icon = icon,
            interactables = interactables
            
        )
        
        self.item_type : Item.Type = item_type
        self.pickUpInteractable = PickUpInteractable()
        self.pickUpInteractable.parent = self
        
        self.dropInteractable = DropInteractable()
        self.dropInteractable.parent = self
           
    def get_interactables(self) -> set[Interactable]:
        if self.inInventory:
            return self.interactables + [self.dropInteractable]
        else:
            return self.interactables + [self.pickUpInteractable]
            
    @property
    def inInventory(self):
        return isinstance(self.parent,Inventory)
    
    def set_interactables(self, interactables:set[Interactable]):
        self.interactables = interactables
        
        
class Equipable(Item):
    def __init__(self,
                 *, x: int = 0,
                 y: int = 0,
                 char: str = "?",
                 color: Tuple[int] = (255, 255, 255),
                 name: str = "<Unnamed>",
                 description: str = "<Missing Description>",
                 icon: str = "assets/sprites/red_egg.png",
                 interactables: list[Interactable] = [],
                 eq_type : Equipment.Type,
                 effect : Optional[Callable[[Action,any]]] = None,
                 hp_bonus = 0,
                 power_bonus = 0,
                 defense_bonus = 0,
                 magic_bonus = 0):
        super().__init__(x=x,
                         y=y,
                         char=char,
                         color=color,
                         name=name,
                         description=description,
                         icon=icon,
                         interactables=interactables)
        
        self.equipped = False
        self.eq_type = eq_type
        
        self.equipInteractable = EquipInteractable()
        self.equipInteractable.parent = self
        
        self.unequipInteractable = UnequipInteractable()
        self.unequipInteractable.parent = self
        
        self.effect = effect
        
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.hp_bonus = hp_bonus
        self.magic_bonus = magic_bonus
        
    
    def get_interactables(self) -> set[Interactable]:
        itemInter = super().get_interactables()
        
        if self.equipped:
            return [self.unequipInteractable] + itemInter
        else:
            return [self.equipInteractable] + itemInter
        
    def has_effect(self):
        return self.effect is not None
    
    def activate_effect(self,action : Action, context_value=None):
        self.effect(action,context_value)
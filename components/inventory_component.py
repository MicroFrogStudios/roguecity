from __future__ import annotations

from enum import Enum
from typing import List, TYPE_CHECKING, Optional

from components.base_component import BaseComponent
import exceptions

if TYPE_CHECKING:
    from classes.actor import Actor
    from classes.item import Item, Equipable


class Inventory(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[Item] = []

    def drop(self, item: Item) -> None:
        """
        Removes an item from the inventory and restores it to the game map, at the player's current location.
        """
        if hasattr(item,"eq_type"):
            item : Equipable = item
            
            if self.parent.equipment.slots[item.eq_type] == item:
                self.parent.equipment.unequip(item.eq_type)
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.gamemap)
        
    def add(self,item : Item):
        if len(self.items) >= self.capacity:
                    raise exceptions.Impossible("Your inventory is full.")
        self.engine.game_map.entities.remove(item)
        item.parent = self
        self.items.append(item)
        
        
class Equipment(BaseComponent):
    class eq_type(Enum):
        BODY = "body"
        WEAPON = "weapon" 
        AMULET = "amulet"
        STAFF = "staff" 
    def __init__(self) -> None:
        self.slots : dict[self.eq_type,Optional[Equipable]]= {
            self.eq_type.BODY: None,
            self.eq_type.WEAPON : None,
            self.eq_type.AMULET : None,
            self.eq_type.STAFF: None
        }

    @property
    def body(self):
        return self.slots[self.eq_type.BODY]
    
    @property
    def weapon(self):
        return self.slots[self.eq_type.WEAPON]
    
    @property
    def amulet(self):
        return self.slots[self.eq_type.AMULET]
    
    @property
    def staff(self):
        return self.slots[self.eq_type.STAFF]
        
    def equip(self,item : Equipable):
        """put item in slot, retag the other maybe"""
        current_slot = self.slots[item.eq_type]
        if current_slot is not None:
            current_slot.equipped = False   
            
        item.equipped = True
        self.slots[item.eq_type] = item
        
    def unequip(self, slot: Equipment.eq_type):
        self.slots[slot].equipped = False
        self.slots[slot] = None
            
            
        
        
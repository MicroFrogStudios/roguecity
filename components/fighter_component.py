from __future__ import annotations

from typing import TYPE_CHECKING

from enums.render_order import RenderOrder
import enums.color as color
if TYPE_CHECKING:
    from classes.actor import Actor
    from actions import Action
from components.base_component import BaseComponent


class Fighter(BaseComponent):
    parent: Actor
    def __init__(self, hp: int, defense: int, power: int,magic:int):
        self.base_max_hp = hp
        self._hp = hp
        self.defense = defense
        self.power = power
        self.magic = magic

    @property
    def hp(self) -> int:
        return self._hp 
    
    @property
    def max_hp(self) -> int:
        return self.base_max_hp + self.hp_bonus
    
    def att_bonus(self,att):
        total_bonus = 0
        for e in self.parent.equipment.slots.values():
            if e is not None:
                total_bonus += getattr(e,f"{att}_bonus")        
        return total_bonus
        
    
    
    
    @property
    def power_bonus(self):
        return self.att_bonus("power")
    
    @property
    def defense_bonus(self):
        return self.att_bonus("defense")
    
    @property
    def hp_bonus(self):
        return self.att_bonus("hp")
    
    @property
    def magic_bonus(self):
        return self.att_bonus("magic")

    @property
    def power_total(self):
        return self.power + self.att_bonus("power")
    
    @property
    def defense_total(self):
        return self.defense + self.att_bonus("defense")
    
    @property
    def hp_total(self):
        return self.hp + self.att_bonus("hp")
    
    @property
    def magic_total(self):
        return self.magic + self.att_bonus("magic")
    @property
    def weapon(self):
        return self.parent.equipment.weapon
    
    @property
    def armor(self):
        return self.parent.equipment.armor
    
    @property
    def amulet(self):
        return self.parent.equipment.amulet
    
    @property
    def staff(self):
        return self.parent.equipment.staff
    
    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    def die(self) -> None:
        if self.engine.player is self.parent:
            death_message = "You died!"
            death_msg_color = color.player_die
            
        else:
            death_message = f"{self.parent.name} is dead!"
            death_msg_color = color.enemy_die

        # self.parent.char = "%"
        self.parent.bgColor = self.parent.blood_color
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.message_log.add_message(death_message,death_msg_color)
        self.parent.drop_loot(self.engine.game_map)
        
    
    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount

        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
    
    def calc_damage(self,enemy :Fighter):
        return self.power + self.power_bonus - enemy.defense - enemy.defense_bonus
    
    def weapon_special_effect(self, action :Action, damage:int):
        
        if self.weapon and self.weapon.has_effect():
            damage = self.weapon.activate_effect(action,damage)
        return damage
            
    def armor_special_effect(self,action :Action, damage:int):
        if self.armor and self.armor.has_effect():
            damage = self.armor.activate_effect(action,damage)
        return damage
       
    def amulet_special_effect(self):
        if self.amulet and self.amulet.has_effect():
            self.amulet.activate_effect(None)
        
    def staff_special_effect(self,action):
        if self.staff and self.staff.has_effect():
            self.staff.activate_effect(action)
        
        


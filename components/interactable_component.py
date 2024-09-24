from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions

from components.interactor_component import Interactor
import enums.color as color
from components import ai
from components.inventory_component import Inventory
from components.base_component import BaseComponent
from exceptions import Impossible



if TYPE_CHECKING:
    from classes.item import Item
    from classes.actor import Actor

import exceptions
from handlers.input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler,
    SingleRangedAttackHandler,
)


class Interactable(BaseComponent):


    # def __init__(self, name, tooltip) -> None:
    #     super().__init__()
    #     self.name = name
    #     self.tooltip = tooltip

    # def __init__(self,name:str, tooltip:str = "") -> None:
    #     self.name=name
    #     self.tooltip=tooltip
    name = "<NULL>"
    def get_action(self, activator: Interactor) -> Optional[ActionOrHandler]:
        """Try to return the action for this item."""
        return actions.InteractiveAction(activator,self)

    def check_player_activable(self) -> bool:
        """
        Check if this interaction is allowed to activate this turn
        """
        raise NotImplementedError()
    
    def activate(self, action: actions.InteractiveAction) -> None:
        """Invoke this items ability.

        `action` is the context for this activation.
        """
        raise NotImplementedError()

class TalkInteraction():
    name = "TALK"
    parent : Actor
    def __init__(self, *lines :str,ordered = True) -> None:
        self.lines = lines
        self.ordered = ordered
    
    def get_action(self, activator: Interactor) -> Optional[ActionOrHandler]:
        """Try to return the action for this item."""
        return actions.InteractiveAction(activator,self,(self.parent.x,self.parent.y))
    
    def activate(self, action: actions.InteractiveAction) -> None:
        
        target = action.target_actor
        
        
class TauntInteraction(Interactable):
    
    name = "TAUNT"
    parent : Actor
    def get_action(self, activator: Interactor) -> Optional[ActionOrHandler]:
        """Try to return the action for this item."""
        return actions.InteractiveAction(activator,self,(self.parent.x,self.parent.y))
    
    def activate(self, action: actions.InteractiveAction) -> None:
        
        target = action.target_actor
        if action.entity is action.engine.player:
            
            self.engine.message_log.add_message(
                f"you taunt the {target.name}",
                color.enemy_atk)
        else:
             self.engine.message_log.add_message(
                f"The {action.entity.name} taunts the {target.name}",
                color.enemy_atk)
        
    def check_player_activable(self) -> bool:        
        return self.parent.is_alive and self.engine.player.distance(self.parent.x,self.parent.y) < 5

class ConsumeInteractable(Interactable):
    parent: Item

    # def get_action(self, consumer: Interactor) -> Optional[ActionOrHandler]:
    #     """Try to return the action for this item."""
    #     return actions.ItemAction(consumer, self.parent)
    
    def consume(self) -> None:
        """Remove the consumed item from its containing inventory or map."""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, Inventory):
            inventory.items.remove(entity)
        else:
            #This is in current map
            self.engine.game_map.entities.remove(entity)
            
    def check_player_activable(self) -> bool:
        return self.engine.player.distance(self.parent.x,self.parent.y) < 2


class EatInteraction(ConsumeInteractable):
    name = "EAT"
    def __init__(self, amount: int):
        self.amount = amount
    def activate(self, action: actions.InteractiveAction) -> None:
        consumer = action.entity
        if not hasattr(consumer, "interactor"):
            raise Impossible(f"{consumer.name} cannot perform eat")
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP!",
                color.health_recovered,
            )
            self.consume()
        else:
            raise Impossible(f"Your health is already full.")
        

class PickUpInteractable(Interactable):
    parent: Item
    name = "PICK UP"

    def check_player_activable(self) -> bool:
        return self.engine.player.distance(self.parent.x,self.parent.y) < 2
    
    def activate(self, action: actions.InteractiveAction) -> None:
        inventory = action.entity.inventory
        if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")
        self.engine.game_map.entities.remove(self.parent)
        self.parent.parent = action.entity.inventory
        inventory.items.append(self.parent)
        self.engine.message_log.add_message(f"You picked up the {self.parent.name}!")


class DropInteractable(Interactable):
    parent: Item
    name = "DROP"
    def activate(self, action: actions.InteractiveAction) -> None:
        action.entity.inventory.drop(self.parent)


class scrollCastInteractable(ConsumeInteractable):
    name = "CAST"
        
class LightningDamageConsumable(scrollCastInteractable):

    def __init__(self, damage: int, maximum_range: int):
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: actions.InteractiveAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            self.engine.message_log.add_message(
                f"A lighting bolt strikes the {target.name} with a loud thunder, for {self.damage} damage!"
            )
            target.fighter.take_damage(self.damage)
            self.consume()
        else:
            raise Impossible("No enemy is close enough to strike.")
        
class ConfusionConsumable(scrollCastInteractable):
    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def get_action(self, activator: Interactor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.InteractiveAction(activator,self, xy),
        )
        

    def activate(self, action: actions.InteractiveAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot confuse yourself!")

        self.engine.message_log.add_message(
            f"The eyes of the {target.name} look vacant, as it starts to stumble around!",
            color.status_effect_applied,
        )
        target.ai = ai.ConfusedEnemy(
            entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns,
        )
        self.consume()

class FireballDamageConsumable(scrollCastInteractable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, activator: Interactor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.InteractiveAction(activator, self, xy),
        )

    def activate(self, action: actions.InteractiveAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")

        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(
                    f"The {actor.name} is engulfed in a fiery explosion, taking {self.damage} damage!"
                )
                actor.fighter.take_damage(self.damage)
                targets_hit = True

        if not targets_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()



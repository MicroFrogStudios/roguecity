from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions

from classes.dialogue import Dialogue


import enums.color as color
from components import ai
from components.inventory_component import Inventory
from components.base_component import BaseComponent
from enums.status_effects import statusEffect
from exceptions import Impossible



if TYPE_CHECKING:
    from components.interactor_component import Interactor
    from classes.item import Item
    from classes.actor import Actor
    from classes.prop import Prop
    from classes.item import Equipable

import random
from handlers.input_handlers import (
    ActionOrHandler,
    AreaRangedAttackHandler,
    DialogueMessage,
    SingleRangedAttackHandler,
)


class Interactable(BaseComponent):


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
        if statusEffect.INVISIBLE in action.entity.fighter.status:
            action.entity.fighter.status.remove(statusEffect.INVISIBLE)

class ActorInteraction(Interactable):
    
    parent : Actor
    def get_action(self, activator: Interactor) -> Optional[ActionOrHandler]:
        """Try to return the action for this item."""
        return actions.InteractiveAction(activator,self,(self.parent.x,self.parent.y))
    
    def check_player_activable(self) -> bool:
        return self.parent.is_alive and self.engine.player.distance(self.parent.x,self.parent.y) < 5 and not self.parent.fighter.status


    
class TalkInteraction(ActorInteraction):
    name = "TALK"
    
    def __init__(self, dialogue :Dialogue) -> None:
        self.dialogue = dialogue
        
    def get_action(self, activator):
        self.talked_line = self.dialogue.get_next_line(self.engine,self)
        return DialogueMessage(self.engine,self.talked_line, super().get_action(activator))

    def check_player_activable(self) -> bool:
        return super().check_player_activable() and not self.parent.hostile

    
    def activate(self, action: actions.InteractiveAction) -> None:
        super().activate(action)
        
        self.engine.message_log.add_message(f"The {self.parent.name} says: {self.talked_line}",color.welcome_text)


class GiveFood(ActorInteraction):
    name = "FEED"

    def check_player_activable(self) -> bool:        
        return  self.parent.is_alive and self.engine.player.distance(self.parent.x,self.parent.y) < 4 and self.engine.player.inventory.has_food() and not self.parent.fighter.status

    def activate(self, action: actions.InteractiveAction) -> None:
        super().activate(action)
        feeder = action.entity
        target = action.target_actor
        
        for item in feeder.inventory.items:
            if item.item_type.value == "FOOD":
                feeder.inventory.items.remove(item)
                break

        self.engine.message_log.add_message(f"you feed the {target.name}. They enter in a trance while eating in a frenzy.",color.welcome_text)
        target.ai = ai.FeastingEnemy(target,target.ai)
        target.fighter.status.add(statusEffect.STUNNED)
        self.engine.stats.hungries_feed+=1

class AssaultInteraction(ActorInteraction):
    name = "STRIKE"
    
    def __init__(self, cry = "What are you doing?!",radius = 5) -> None:
        self.cry = cry
        self.radius = radius
        
    def check_player_activable(self) -> bool:        
        return self.parent.is_alive and self.engine.player.distance(self.parent.x,self.parent.y) < 2

    def activate(self, action: actions.InteractiveAction) -> None:
        super().activate(action)
        target = action.target_actor
        

        (x,y) = action.target_xy
        dx = x - action.entity.x
        dy = y - action.entity.y
        actions.MeleeAction(action.entity,dx,dy).perform()
        target.turn_hostile()
        self.engine.message_log.add_message(f"The {self.parent.name} says: {self.cry}")

class ScareInteraction(ActorInteraction):
    name = "SPOOK"

    def check_player_activable(self) -> bool:        
        return self.parent.is_alive and self.engine.player.distance(self.parent.x,self.parent.y) < 2 and not isinstance(self.parent.ai,ScareInteraction) and not self.parent.fighter.status

    def activate(self, action: actions.InteractiveAction) -> None:
        super().activate(action)
        target = action.target_actor
        target.ai = ai.StunnedAi(target,target.ai,4)
        target.fighter.status.add(statusEffect.STUNNED)
        self.engine.message_log.add_message(
            f"The {target.name} is so spooked it froze in place!",
            color.status_effect_applied,
        )
        self.engine.stats.wizzo_scares+=1


class BiteInteraction(ActorInteraction):
    name = "BITE"

    def check_player_activable(self) -> bool:        
        return self.parent.is_alive and self.engine.player.distance(self.parent.x,self.parent.y) < 2 and not self.parent.fighter.status


    def activate(self, action: actions.InteractiveAction) -> None:
        super().activate(action)
        target = action.target_actor
        if action.entity is action.engine.player:
            
            self.engine.message_log.add_message(
                f"you bite the {target.name}",
                color.enemy_atk)
        else:
             self.engine.message_log.add_message(
                f"The {action.entity.name} bites the {target.name}",
                color.enemy_atk)
             
        
        rand = random.randint(0,100)
        if rand > 60:
            self.engine.message_log.add_message("you recover some HP!")
            action.entity.fighter.heal(5)
        elif rand > 35:
            self.engine.message_log.add_message("you ate poison, you lost 2 HP")
            action.entity.fighter.take_damage(2)
        elif rand > 10:
            self.engine.message_log.add_message("you feel dizzy...")
            self.engine.player_controller.turns_confused += 10
            self.engine.player.fighter.status.add(statusEffect.CONFUSED)
            
        elif rand >= 0:
            self.engine.message_log.add_message("Your body is becoming translucent")
            self.engine.player_controller.turns_invisible += 50
            self.engine.player.fighter.status.add(statusEffect.INVISIBLE)
        target.turn_hostile()
        target.fighter.take_damage(1)
        self.engine.stats.shrooms_bites+=1

class TauntInteraction(ActorInteraction):
    
    name = "TAUNT"
    
    def __init__(self, response = "...") -> None:
        self.response = response
    def activate(self, action: actions.InteractiveAction) -> None:
        super().activate(action)
        target = action.target_actor
        if action.entity is action.engine.player:
            
            self.engine.message_log.add_message(
                f"you taunt the {target.name}",
                color.enemy_atk)
        else:
             self.engine.message_log.add_message(
                f"The {action.entity.name} taunts the {target.name}",
                color.enemy_atk)
             
        self.engine.message_log.add_message(f"The {self.parent.name} says: {self.response}")
        target.actor_type = "CRITTER"
        target.turn_hostile()

class PetInteraction(ActorInteraction):
    
    name = "PET"
    def __init__(self, response = "<3") -> None:
        self.response = response
        
    def activate(self, action: actions.InteractiveAction) -> None:
        super().activate(action)
        target = action.target_actor
        if action.entity is action.engine.player:
            
            self.engine.message_log.add_message(
                f"you pet the {target.name}",
                color.white)
            self.engine.stats.rat_pets+=1
        else:
             self.engine.message_log.add_message(
                f"The {action.entity.name} pets the {target.name}",
                color.white)
        self.engine.message_log.add_message(f"The {self.parent.name} says: {self.response}")
        
        target.friendly_ai = ai.FollowNeutral(target,action.entity,2)
        target.turn_friendly()
        target.actor_type = action.entity.actor_type
    
    def check_player_activable(self):
        return self.parent.is_alive and self.engine.player.distance(self.parent.x,self.parent.y) < 2 and not self.parent.fighter.status

class PropInteraction(Interactable):
    parent: Prop

    def check_player_activable(self) -> bool:
        return self.engine.player.distance(self.parent.x,self.parent.y) < 2

class OpenInteractable(PropInteraction):
    name= "OPEN"
    def activate(self, action: actions.InteractiveAction) -> None:
        import factories.entity_factory as factory
        for i in action.entity.inventory.items:
            if i.name == factory.last_key.name:
                self.engine.win()
                return
        else:
            self.engine.message_log.add_message(
                "You need a key to open this", color.invalid
            )

class DescendInteractable(PropInteraction):
    name = "GO DOWN"
    def activate(self, action: actions.InteractiveAction) -> None:
        self.engine.game_world.descend()
        self.engine.message_log.add_message(
                "You descend the staircase.", color.descend
            )
        
class AscendInteractable(PropInteraction):
    name = "GO UP"
    def activate(self, action: actions.InteractiveAction) -> None:
        self.engine.game_world.ascend()
        self.engine.message_log.add_message(
                "You ascend the staircase.", color.descend
            )
        

class ItemInteraction(Interactable):
    parent: Item
    
    def check_player_activable(self) -> bool:
        return self.engine.player.distance(self.parent.x,self.parent.y) < 2

      
class ConsumeInteractable(ItemInteraction):

    
    def consume(self) -> None:
        """Remove the consumed item from its containing inventory or map."""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, Inventory):
            inventory.items.remove(entity)
        else:
            #This is in current map
            self.engine.game_map.entities.remove(entity)
        if entity.item_type.value == "SCROLL":
            self.engine.stats.scrolls_cast+=1
        if entity.item_type.value == "FOOD":
            self.engine.stats.food_eaten+=1
            
    

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
        



class PickUpInteractable(ItemInteraction):

    name = "PICK UP"
    
    def activate(self, action: actions.InteractiveAction) -> None:

        action.entity.inventory.add(self.parent)
        self.engine.message_log.add_message(f"You picked up the {self.parent.name}!")

class HatchInteraction(ItemInteraction):
    name= "HATCH"
    def activate(self, action: actions.InteractiveAction) -> None:
        if self.engine.game_world.current_floor <= -5:
            from factories.entity_factory import microfrog
            action.entity.inventory.items.remove(self.parent)
            microfrog.place(action.entity.x,action.entity.y,self.engine.game_map)
            action.entity.inventory.add(microfrog)
            self.engine.stats.frogs_hatched+=1
            self.engine.message_log.add_message(f"The egg hatched!!")
        else:
            self.engine.message_log.add_message(f"It doesn't look ready yet.")

class DropInteractable(ItemInteraction):
    name = "DROP"
    def activate(self, action: actions.InteractiveAction) -> None:
        action.entity.inventory.drop(self.parent)
        self.engine.message_log.add_message(f"You dropped the {self.parent.name}.")

class EquipInteractable(ItemInteraction):
    name = "EQUIP"
    parent : Equipable
    

    
    def activate(self, action: actions.InteractiveAction) -> None:
        """tries to equip the item, if it is in the ground, add to the inventory first, if full, you cant equip it"""
        item = self.parent
        equipment = action.entity.equipment

        if not item.inInventory:
            inventory = action.entity.inventory
            inventory.add(item)            
        
        equipment.equip(item)
        self.engine.message_log.add_message(f"You equip the {item.name}!")
        
class UnequipInteractable(ItemInteraction):
    name = "UNEQUIP"
    parent : Equipable
    
    def activate(self, action: actions.InteractiveAction) -> None:
        """tries to equip the item, if it is in the ground, add to the inventory first, if full, you cant equip it"""
        item = self.parent
        equipment = action.entity.equipment

        if not item.inInventory:
            raise Impossible("How did you manage to unequip an object in the ground???")            
        
        equipment.unequip(item.eq_type)
        self.engine.message_log.add_message(f"You unequip the {item.name}!")
        
        
class scrollCastInteractable(ConsumeInteractable):
    name = "CAST"
        
class LightningDamageConsumable(scrollCastInteractable):

    def __init__(self, damage: int, maximum_range: int):
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: actions.InteractiveAction) -> None:
        
        super().activate(action)
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y] and actor is not self.engine.player_follower:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            self.engine.message_log.add_message(
                f"A lighting bolt strikes the {target.name} with a loud thunder, for {self.damage*action.entity.fighter.magic_total} damage!"
            )
            target.fighter.take_damage(self.damage * action.entity.fighter.magic_total)
            self.consume()
            if actor is not self.engine.player and actor is not self.engine.player_follower and actor.distance(target.x,target.y) <= 20 and actor.actor_type == target.actor_type and self.engine.game_map.visible[actor.x, actor.y] and not actor.fighter.status:
                    actor.turn_hostile()
        else:
            raise Impossible("No enemy is close enough to strike.")


class TeleportConsumable(scrollCastInteractable):
    
    def get_action(self, activator: Interactor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.InteractiveAction(activator,self, xy),
        )
    
    def activate(self, action):
        consumer = action.entity
        target_xy = action.target_xy
        if self.engine.game_map.explored[target_xy] and self.engine.game_map.tiles[target_xy]['walkable']:
            self.engine.message_log.add_message(
            "You teleport away!", color.magic_green
            )
            consumer.place(*target_xy)
            self.consume()
        else: 
            raise Impossible(
            "You cant teleport here"
            )

class InvisibleConsumable(scrollCastInteractable):

    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def activate(self, action):
        consumer = action.entity
        target = consumer
        target.fighter.status.add(statusEffect.INVISIBLE)
        if target is self.engine.player:
            self.engine.player_controller.turns_invisible += self.number_of_turns*target.fighter.magic_total
        self.consume()

class FreezeConsumable(scrollCastInteractable):

    def get_action(self, activator: Interactor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.InteractiveAction(activator,self, xy),
        )
    
    def activate(self, action: actions.InteractiveAction) -> None:
        super().activate(action)
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot freeze yourself!")

        self.engine.message_log.add_message(
            f"The {target.name} freezes completely!",
            color.cold_blue,
        )
        
        target.ai = ai.FrozenEnemy(
            entity=target, previous_ai=target.ai,
        )
        target.fighter.status.add(statusEffect.FROZEN)
        self.consume()



class ThrowInteraction(ConsumeInteractable): 
    name = "THROW"

    def __init__(self, damage: int):
        self.damage = damage

    def get_action(self, activator: Interactor) -> SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.InteractiveAction(activator,self, xy),
        )
        

    def activate(self, action: actions.InteractiveAction) -> None:
        super().activate(action)
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select an enemy to target.")
        if target is consumer:
            raise Impossible("You cannot throw it on yourself!")

        self.engine.message_log.add_message(
            f"You throw the {self.parent.name} at the {target.name}!",
            color.player_atk,
        )
        damage = consumer.fighter.calc_damage(target.fighter) - consumer.fighter.power_bonus + self.damage
        if damage > 0:
            if statusEffect.FROZEN in target.fighter.status:
                damage *= consumer.fighter.magic_total+1
                self.engine.message_log.add_message(f"The ice encasing {target.name} shatters, dealing x{consumer.fighter.magic_total+1}!",color.player_atk)
                target.turn_hostile()
                target.fighter.status.remove(statusEffect.FROZEN)
            target.fighter.take_damage(damage)
            self.engine.message_log.add_message(
            f"The {self.parent.name} hits the {target.name} doing {damage} damage!",
            color.player_atk)
        else:
            self.engine.message_log.add_message(
            f"The {self.parent.name} misses the {target.name}",
            color.player_atk)
        if consumer is self.engine.player:
            for actor in self.engine.game_map.actors:
                if actor is not self.engine.player and actor is not self.engine.player_follower and actor.distance(target.x,target.y) <= 20 and actor.actor_type == target.actor_type and self.engine.game_map.visible[actor.x, actor.y] and not actor.fighter.status:
                    actor.turn_hostile()
        self.consume()

class ConfusionConsumable(scrollCastInteractable):
    def __init__(self, number_of_turns: int,radius: int):
        self.number_of_turns = number_of_turns
        self.radius = radius

    def get_action(self, activator: Interactor) -> AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius * activator.parent.fighter.magic_total,
            callback=lambda xy: actions.InteractiveAction(activator, self, xy),
            char='?',
            color=self.parent.fgColor
        )
        

    def activate(self, action: actions.InteractiveAction) -> None:
        super().activate(action)
        
        consumer = action.entity
        

        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")

        targets_hit = False
        actors_hit : list[Actor] = []
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius * action.entity.fighter.magic_total and actor is not consumer:
                actors_hit.append(actor)
                targets_hit = True

        for actor in actors_hit:
        # if target is consumer:
        #     raise Impossible("You cannot confuse yourself!")

            self.engine.message_log.add_message(
                f"The eyes of the {actor.name} look vacant, as it starts to stumble around!",
                color.status_effect_applied,
        )
            actor.ai = ai.ConfusedEnemy(
                entity=actor, previous_ai=actor.ai, turns_remaining=self.number_of_turns,
            )
            actor.fighter.status.add(statusEffect.CONFUSED)
        if not targets_hit:
            raise Impossible("There are no valid targets in the radius.")
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
            char='‼',
            color=self.parent.fgColor
        )



    def activate(self, action: actions.InteractiveAction) -> None:
        super().activate(action)
        
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")

        targets_hit = False
        actors_hit : list[Actor] = []
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                actors_hit.append(actor)
                targets_hit = True

        for actor in actors_hit:
            self.engine.message_log.add_message(
                    f"The {actor.name} is engulfed in a fiery explosion, taking {self.damage * action.entity.fighter.magic_total} damage!"
                )
            actor.fighter.take_damage(self.damage * action.entity.fighter.magic_total)
            if actor is not self.engine.player and actor is not self.engine.player_follower and self.engine.game_map.visible[actor.x, actor.y] and not actor.fighter.status:
                    actor.turn_hostile()
        

        if not targets_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()



from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

from components.interactor_component import Interactor
import enums.color as color
import exceptions
if TYPE_CHECKING:
    from engine import Engine
    from classes.entity import Entity
    from classes.actor import Actor
    from classes.item import Item
    from components.interactable_component import Interactable

class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.parent.engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `engine` is the scope this action is being performed in.

        `entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class ActionWithDirection(Action):
    def __init__(self, actor: Actor, dx: int, dy: int):
        super().__init__(actor)
        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination.."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)
    
    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()
    
class MovementAction(ActionWithDirection):

    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy
        self.engine
        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise exceptions.Impossible("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination is out of bounds.
            raise exceptions.Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is out of bounds.
            raise exceptions.Impossible("That way is blocked.")

        self.entity.move(self.dx, self.dy)

class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        
        if not target:
            raise exceptions.Impossible("Nothing to attack.")

        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk
        if damage > 0:
            
            self.engine.message_log.add_message(f"{attack_desc} for {damage} hit points.",attack_color)
            target.fighter.hp -= damage
            if target == self.engine.player:
                self.engine.player_controller.interrupt()
        else:
            self.engine.message_log.add_message(f"{attack_desc} but does no damage.",attack_color)

class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor and self.target_actor.hostile:
            return MeleeAction(self.entity, self.dx, self.dy).perform()

        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()
        

class WaitAction(Action):
    def perform(self) -> None:
        pass


class InteractiveAction(Action):
    
    def __init__(
        self, interactor: Interactor, interactable : Interactable, target_xy: Optional[Tuple[int, int]] = None
    ):
        super().__init__(interactor.parent)
        self.interactable = interactable
        if  not target_xy :
            target_xy = interactor.parent.x,interactor.parent.y
        else:
            self.target_xy = target_xy
            
    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        self.interactable.activate(self)
        
    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)
    
    @property
    def target_entity(self) -> Optional[Entity]:
        NotImplemented
        return self.engine.game_map.entities

    @property
    def target_item(self) -> Optional[Item]:
        NotImplemented


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f"You picked up the {item.name}!")
                return

        raise exceptions.Impossible("There is nothing here to pick up.")


class TakeStairsAction(Action):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.engine.game_world.generate_floor()
            self.engine.message_log.add_message(
                "You descend the staircase.", color.descend
            )
        else:
            raise exceptions.Impossible("There are no stairs here.")
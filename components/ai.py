from __future__ import annotations

from typing import List, Tuple, Optional, TYPE_CHECKING
import random
import numpy as np  # type: ignore
import tcod

from actions import Action, MeleeAction, MovementAction, WaitAction, BumpAction



if TYPE_CHECKING:
    from classes.actor import Actor
    from classes.entity import Entity
    from classes.item import Item

class BaseAI(Action):


    entity: Actor
    
    def __init__(self, entity = None):
        super().__init__(entity)
        
    def perform(self) -> None:
        raise NotImplementedError()

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.
        cost = np.array(self.entity.parent.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.parent.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[entity.x, entity.y] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]


class PlayerAI(BaseAI):
    
    
    def finished(self):
        raise NotImplementedError()
    
class PlayerInteract(PlayerAI):
    
    def __init__(self, entity: Actor,target : Entity):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []
        self.target : Entity = target
        self._finished = False

    def finished(self):
        return self._finished
    
    def perform(self) -> None:
        """Follows the target at certain distance"""
        if self.target is None:
            return None
        dx = self.target.x - self.entity.x
        dy = self.target.y - self.entity.y
        distance = max(abs(dx), abs(dy))  # Chebyshev distance.

        
        if distance <= 1:
            self._finished = True
            if hasattr(self.target,"pickUpInteractable"):
                self.target : Item
                return self.target.pickUpInteractable.get_action(self.entity.interactor).perform()
            elif hasattr(self.target,"hostile") and self.target.hostile:
                return MeleeAction(self.entity, dx, dy).perform()
        
        self.path = self.get_path_to(self.target.x, self.target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            
            return MovementAction(
                self.entity, (dest_x - self.entity.x), (dest_y - self.entity.y),
            ).perform()
        
        self.target = None
    
class PlayerPathing(PlayerAI):
    def __init__(self, entity: Actor, target):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []
        self.target : Tuple[int,int] = target
    
    
    def finished(self):
        return self.target is None
    def perform(self) -> None:
        """Follows the target at certain distance"""
        if self.target is None:
            return None
        
        self.path = self.get_path_to(self.target[0], self.target[1])

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            
            return MovementAction(
                self.entity, (dest_x - self.entity.x), (dest_y - self.entity.y),
            ).perform()
        
        self.target = None
    
class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor=None):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))  # Chebyshev distance.

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()

            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
            ).perform()

        return WaitAction(self.entity).perform()
    
class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for a given number of turns, then revert back to its previous AI.
    If an actor occupies a tile it is randomly moving into, it will attack.
    """

    def __init__(
        self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int
    ):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        # Revert the AI back to the original state if the effect has run its course.
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer confused."
            )
            self.entity.ai = self.previous_ai
        else:
            # Pick a random direction
            direction_x, direction_y = random.choice(
                [
                    (-1, -1),  # Northwest
                    (0, -1),  # North
                    (1, -1),  # Northeast
                    (-1, 0),  # West
                    (1, 0),  # East
                    (-1, 1),  # Southwest
                    (0, 1),  # South
                    (1, 1),  # Southeast
                ]
            )

            self.turns_remaining -= 1

            # The actor will either try to move or attack in the chosen random direction.
            # Its possible the actor will just bump into the wall, wasting a turn.
            return BumpAction(self.entity, direction_x, direction_y,).perform()
        
class IdleNeutral(BaseAI):
    
    def perform(self) -> None:
        """Does nothing as its the idle action"""
        pass
    
class FollowNeutral(BaseAI):
    
    def __init__(self, entity: Actor = None,target = None, follow_distance=3,):
        super().__init__(entity)
        self.target = target
        self.follow_distance = follow_distance
        self.path: List[Tuple[int, int]] = []
    
    def perform(self) -> None:
        """Follows the target at certain distance"""
        if self.target == None:
            self.target = self.engine.player
        dx = self.target.x - self.entity.x
        dy = self.target.y - self.entity.y
        distance = max(abs(dx), abs(dy))  # Chebyshev distance.

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:

            self.path = self.get_path_to(self.target.x, self.target.y)

        if self.path and distance != self.follow_distance:
            dest_x, dest_y = self.path.pop(0)
            direction = 1 if distance > self.follow_distance else -1
            return MovementAction(
                self.entity, direction*(dest_x - self.entity.x), direction*(dest_y - self.entity.y),
            ).perform()
        
        return WaitAction(self.entity).perform()
    
class RandomGait(BaseAI):
    """
   will move randomly with a given frequency
    """

    def __init__(
        self,  turns_to_move: int,entity: Actor = None
    ):
        super().__init__(entity)
        self.turns_to_move = turns_to_move
        self.turn_counter = turns_to_move
        
        
    def perform(self) -> None:
        # Revert the AI back to the original state if the effect has run its course.
        if self.turn_counter > 0:
            self.turn_counter -= 1
            
        else:
            # Pick a random direction
            direction_x, direction_y = random.choice(
                [
                    (-1, -1),  # Northwest
                    (0, -1),  # North
                    (1, -1),  # Northeast
                    (-1, 0),  # West
                    (1, 0),  # East
                    (-1, 1),  # Southwest
                    (0, 1),  # South
                    (1, 1),  # Southeast
                ]
            )

            self.turn_counter = self.turns_to_move

            # The actor will either try to move or attack in the chosen random direction.
            # Its possible the actor will just bump into the wall, wasting a turn.
            return BumpAction(self.entity, direction_x, direction_y,).perform()
from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np  # type: ignore
from tcod.console import Console
from classes.actor import Actor
from classes.item import Item
import config
import map.tile_types as tile_types
import factories.entity_factory as factory
if TYPE_CHECKING:
    from classes.entity import Entity
    from engine import Engine



class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs.
    """

    def __init__(
        self,
        *,
        engine: Engine,
        map_width: int,
        map_height: int,
        max_rooms: int = 1,
        room_min_size: int = 8,
        room_max_size: int = 12,
        max_monsters_per_room: int = 1,
        max_items_per_room: int = 1,
        current_floor: int = 0
    ):
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.max_monsters_per_room = max_monsters_per_room
        self.max_items_per_room = max_items_per_room

        self.current_floor = current_floor
    
    def tutorial_map(self):
        pass
        # from map.gen.dungeon import generate_level
        # self.engine.game_map = generate_level(8,12,self.map_width, self.map_height,self.engine)
    
    def test_world(self) -> None:
        self.engine.game_map = GameMap(self.engine, self.map_width, self.map_height, entities=[self.engine.player])
        from map.gen.rooms import RectangularRoom
        room = RectangularRoom(1,1,self.map_width-1,self.map_height-1)
        self.engine.game_map.tiles[room.inner] = tile_types.new_floor()
        self.engine.player.place(*room.center, self.engine.game_map)
        from factories.entity_factory import mystery_egg, food, old_man, broken_sword, amulet_health,wooden_staff,worn_outfit
        egg = mystery_egg.spawn(self.engine.game_map,*room.center)
        food.spawn(self.engine.game_map,*room.center)
        broken_sword.spawn(self.engine.game_map,room.center[0]+2,room.center[1]+2)
        amulet_health.spawn(self.engine.game_map,*room.center)
        worn_outfit.spawn(self.engine.game_map,*room.center)
        wooden_staff.spawn(self.engine.game_map,*room.center)
        spawned_old = old_man.spawn(self.engine.game_map,room.center[0],room.center[1]+3)
        spawned_old.inventory.add(egg)

        
        return None
    
    def descend(self) -> None:
        self.current_floor -= 1
        self.generate_floor(False)

    def ascend(self) -> None:
        self.current_floor += 1
        self.generate_floor(True)

    def generate_floor(self, goingUp : bool) -> None:
        from map.gen.dungeon import generate_level
        self.engine.game_map = generate_level(self.room_min_size,
                                              self.room_max_size,
                                              self.map_width,
                                                self.map_height,
                                                self.engine,
                                                goingUp,
                                                self.current_floor)


class GameMap:

    def __init__(self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = (),wall=tile_types.new_wall()):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full(
            (width, height), fill_value=wall, order="F")

        # Tiles the player can currently see
        self.visible = np.full((width, height), fill_value=False, order="F")
        # Tiles the player has seen before
        self.explored = np.full((width, height), fill_value=False, order="F")

        # self.tiles[30:33, 22] = tile_types.new_wall()
        self.downstairs_location = (0, 0)
    
    @property
    def gamemap(self) -> GameMap: 
        return self
    
    @property
    def actors(self) -> Iterator[Actor]:
        yield  from(
            entity for entity in self.entities if isinstance(entity,Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location(self, location_x: int, location_y: int) -> Optional[Entity]:
        for entity in self.entities:
            if entity.blocks_movement and entity.x == location_x and entity.y == location_y:
                return entity

        return None
    
    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None
    
    def closest_visible_entity(self):
        player = self.engine.player
        target = None
        closest_distance = 99.

        for entity in self.entities:
            if entity is not player and self.visible[entity.x, entity.y]:
                distance = player.distance(entity.x, entity.y)

                if distance < closest_distance:
                    target = entity
                    closest_distance = distance
                    
        return target

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height


    def render(self, console: Console) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        
        (x_left,x_right,y_left,y_right) = (self.engine.x_left_ref,self.engine.x_right_ref, self.engine.y_left_ref, self.engine.y_right_ref)

        camera_tiles = self.tiles[x_left:x_right, y_left:y_right]
        camera_visible = self.visible[x_left:x_right, y_left:y_right]
        camera_explored = self.explored[x_left:x_right, y_left:y_right]

        console.rgb[self.engine.camera_x_offset:self.engine.camera_width+ self.engine.camera_x_offset, 0:self.engine.camera_height] = np.select(
            condlist=[camera_visible, camera_explored],
            choicelist=[camera_tiles["light"], camera_tiles["dark"]],
            default=tile_types.SHROUD,
        )
        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )
        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV
            camera_ref_x,camera_ref_y = self.engine.map_to_camera_coordinates(entity.x,entity.y)
            if self.visible[entity.x,entity.y]:
                console.print(camera_ref_x, camera_ref_y, entity.char, fg=entity.fgColor,bg=entity.bgColor)

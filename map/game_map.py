from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np  # type: ignore
from tcod.console import Console
from classes.actor import Actor
from classes.item import Item
import map.tile_types as tile_types

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
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        max_monsters_per_room: int,
        max_items_per_room: int,
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

    def generate_floor(self) -> None:
        from map.gen.dungeon import generate_dungeon

        self.current_floor += 1

        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            max_monsters_per_room=self.max_monsters_per_room,
            max_items_per_room=self.max_items_per_room,
            engine=self.engine,
        )


class GameMap:
    def __init__(self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full(
            (width, height), fill_value=tile_types.new_wall(), order="F")

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

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console, player_x,player_y) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        x_left = player_x-console.width//2
        x_right = player_x+console.width//2

        if x_left < 0:
            x_right =console.width
            x_left = 0
        if x_right > self.width:
            x_left = self.width - console.width
            x_right = self.width

        y_left = player_y-console.height//2
        y_right = player_y+console.height//2
        
        if y_left < 0:
            y_right =console.height
            y_left = 0
        if y_right > self.height:
            y_left = self.height - console.height
            y_right = self.height

        camera_tiles = self.tiles[x_left:x_right, y_left:y_right]
        camera_visible = self.visible[x_left:x_right, y_left:y_right]
        camera_explored = self.explored[x_left:x_right, y_left:y_right]

        console.rgb[0:self.width, 0:self.height] = np.select(
            condlist=[camera_visible, camera_explored],
            choicelist=[camera_tiles["light"], camera_tiles["dark"]],
            default=tile_types.SHROUD,
        )
        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )
        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV
            camera_ref_x =  entity.x - x_left
            camera_ref_y = entity.y - y_left
            if self.visible[entity.x,entity.y]:
                console.print(camera_ref_x, camera_ref_y, entity.char, fg=entity.fgColor,bg=entity.bgColor)

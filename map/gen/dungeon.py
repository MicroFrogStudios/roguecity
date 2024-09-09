from map.game_map import GameMap
import  map.tile_types as tiles
from map.gen.rooms import RectangularRoom, tunnel_between
import random
from typing import List, TYPE_CHECKING
import factories.entity_factories as factory

from engine import Engine

def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    engine: Engine,
    max_monsters_per_room: int,
    max_items_per_room: int

) -> GameMap:
    """Generate a new dungeon map."""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []
    center_of_last_room = (0, 0)

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        # "RectangularRoom" class makes rectangles easier to work with
        new_room = RectangularRoom(x, y, room_width, room_height)

        # Run through the other rooms and see if they intersect with this one.
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue  # This room intersects, so go to the next attempt.
        # If there are no intersections then the room is valid.

        # Dig out this rooms inner area.
        dungeon.tiles[new_room.inner] = tiles.new_floor()
        place_entities(new_room,dungeon,max_monsters_per_room, max_items_per_room)

        if len(rooms) == 0:
            # The first room, where the player starts.
            player.place(*new_room.center, dungeon)
        else:  # All rooms after the first.
            # Dig out a tunnel between this room and the previous one.
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tiles.new_floor()
            center_of_last_room = new_room.center
        dungeon.tiles[center_of_last_room] = tiles.down_stairs
        dungeon.downstairs_location = center_of_last_room
        # Finally, append the new room to the list.
        rooms.append(new_room)

    return dungeon

def place_entities(room: RectangularRoom, dungeon: GameMap, maximum_monsters: int, maximum_items: int
) -> None:
    number_of_monsters = random.randint(0, maximum_monsters)
    number_of_items = random.randint(0,maximum_items)

    for i in range(number_of_monsters):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            if random.random() < 0.8:
                factory.orc.spawn(dungeon,x,y)
            else:
                factory.troll.spawn(dungeon,x,y)

    for i in range(number_of_items):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            item_chance = random.random()

            if item_chance < 0.6:
                factory.food.spawn(dungeon, x, y)
            elif item_chance < 0.8:
                factory.fireball_scroll.spawn(dungeon, x, y)
            elif item_chance < 0.9:
                factory.confusion_scroll.spawn(dungeon, x, y)
            else:
                factory.lightning_scroll.spawn(dungeon, x, y)
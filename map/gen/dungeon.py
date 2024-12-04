from map.game_map import GameMap
import  map.tile_types as tiles
from map.gen.rooms import RectangularRoom, tunnel_between, Point
import random
from typing import List, TYPE_CHECKING
import factories.entity_factory as factory

from engine import Engine



def generate_tutorial(engine:Engine):
    
    player = engine.player
    tutorial_map = GameMap(engine, 200, 200, entities=[player])
    starting_room = RectangularRoom(100-6,200-9,12,8)
    tutorial_map.tiles[starting_room.inner] = tiles.new_floor()
    tutorial_map.tiles[100,200-9] = tiles.new_door()
    second_room = RectangularRoom(100-8,200-23,16,14)
    tutorial_map.tiles[second_room.inner] = tiles.new_floor()
    player.place(*starting_room.center,tutorial_map)
    
    
    return tutorial_map


def generate_level(
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    engine: Engine,
    level: int,
    goingUp: bool 
)-> GameMap:
    """Generate a new dungeon map of the selected floor."""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])
    stair_room_dim = 6
    
    left_stair_x = map_width//6 - stair_room_dim//2
    left_stair_y = map_height//2 - stair_room_dim//2
    left_stair_room = RectangularRoom(left_stair_x,left_stair_y,stair_room_dim,stair_room_dim)

    dungeon.tiles[left_stair_room.inner] = tiles.new_floor()
    dungeon.tiles[left_stair_x + stair_room_dim,left_stair_room.center[1]] = tiles.new_door()

    right_stair_x = map_width//6*5 - stair_room_dim//2
    right_stair_y = left_stair_y
    right_stair_room = RectangularRoom(right_stair_x,right_stair_y,stair_room_dim,stair_room_dim)

    dungeon.tiles[right_stair_room.inner] = tiles.new_floor()
    dungeon.tiles[right_stair_room.center[0]-stair_room_dim//2,right_stair_room.center[1]] = tiles.new_door()
    hall_width =right_stair_x- left_stair_x - stair_room_dim
    main_hall = RectangularRoom(left_stair_x + stair_room_dim,left_stair_y+1,hall_width,4)
    dungeon.tiles[main_hall.inner] = tiles.new_floor()

    north_placed_rooms = [main_hall]
    south_placed_rooms = [main_hall]
    n_tries = 20
    n_center_candidates = 60
    
    leftmost_x = left_stair_x + stair_room_dim + room_min_size//2
    leftmost_y = left_stair_y - room_min_size//2
    

    for i in range(n_tries):
        # north
        center_candidates =generate_candidate_points(
                                leftmost_x,
                                room_min_size//2,
                                right_stair_x - 1 - room_min_size//2,
                                left_stair_y - room_min_size//2, 
                                n_center_candidates)
        generate_more_rooms(dungeon,north_placed_rooms,center_candidates,room_min_size,room_max_size)
        
        #south
        center_candidates =generate_candidate_points(
                                leftmost_x,
                                main_hall.y2 + room_min_size//2,
                                right_stair_x - 1 - room_min_size//2,
                                dungeon.height - room_min_size//2, 
                                n_center_candidates)
        generate_more_rooms(dungeon,south_placed_rooms,center_candidates,room_min_size,room_max_size)

        
        
    for roomA in north_placed_rooms:
        for roomB in north_placed_rooms:
            if roomA is not roomB:
                door = roomA.touchMiddlePoint(roomB)
                if door is not None:
                    print("connecting adjacent rooms..")
                    dungeon.tiles[door] = tiles.new_door()
    
    for roomA in south_placed_rooms:
        for roomB in south_placed_rooms:
            if roomA is not roomB:
                door = roomA.touchMiddlePoint(roomB)
                if door is not None:
                    print("connecting adjacent rooms..")
                    dungeon.tiles[door] = tiles.new_door()


    print(len(north_placed_rooms)+len(south_placed_rooms)-2)

    factory.down_staircase.spawn(dungeon,*right_stair_room.center)
    factory.up_staircase.spawn(dungeon,*left_stair_room.center)
    if goingUp:
        player.place(*right_stair_room.center, dungeon)
    else:
        player.place(*left_stair_room.center, dungeon)
    return dungeon


def generate_more_rooms(dungeon : GameMap, placed_rooms: list[RectangularRoom],center_candidates : list[Point],room_min_size,room_max_size):
    
    current_room = placed_rooms[random.randint(0,len(placed_rooms)-1)]
    while len(center_candidates) > 0:
        center = Point(*current_room.center)
        nearest_candidate_i = center.nearestToSelf(center_candidates)
        overlap= False
        for room in placed_rooms:
            
            if center_candidates[nearest_candidate_i].inside(room):
                overlap = True
                break
        if overlap:
            del center_candidates[nearest_candidate_i]
            print("candidate discarded for overlap")
            continue

        next_center = center_candidates.pop(nearest_candidate_i) 
        next_room : RectangularRoom  = current_room.adjacentRoomFromCenter(next_center,random.randint(room_min_size,room_max_size))
        if next_room is None:
            print("candidate discarded for nullity")
            continue

        if next_room.height < room_min_size or next_room.width < room_min_size:
            print(f"candidate discarded for smallness: {next_room.width}, {next_room.height}")
            continue
        interesects = False
        for room in placed_rooms:
            if next_room.intersects(room):
                interesects = True
                break
        if interesects:
            print(f"candidate discarded for interesction")
            continue
        if next_room.y1 <= 0 or next_room.x1 <=0 or next_room.y2 > dungeon.height or next_room.x2 > dungeon.width :
            print(f"candidate discarded for going out of bounds")
            continue
        dungeon.tiles[next_room.inner] = tiles.new_floor()
        if not next_room.touching(current_room):
            print(f"candidate discarded for not touching")
            continue
        dungeon.tiles[current_room.touchMiddlePoint(next_room)] = tiles.new_door()
        print(current_room.touchMiddlePoint(next_room))
        place_entities(next_room,dungeon,5, 5)
        placed_rooms.append(next_room)
        current_room = next_room

def generate_candidate_points(x_lower,y_lower, x_upper, y_upper, n_center_candidates ):
    candidates : list[Point] = []
    for i in range(n_center_candidates):
        x = random.randint(x_lower, x_upper)
        y = random.randint(y_lower,y_upper)
        print(f"{x}, {y}")
        candidates.append(Point(x,y))
    return candidates


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
                factory.weak_skuly.spawn(dungeon,x,y)
            else:
                factory.rat_small.spawn(dungeon,x,y)

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
from map.game_map import GameMap
import  map.tile_types as tiles
from map.gen.rooms import RectangularRoom, tunnel_between, Point
import random
from typing import List, TYPE_CHECKING
import factories.entity_factory as factory
import enums.color as color
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


def highest_zone(engine: Engine,map_width,map_height): 
    floor = tiles.new_floor(color.stone_grey_light,color.stone_grey_dark)
    wall = tiles.new_wall(color.stone_grey,color.stone_grey_darker)
    door = tiles.new_door(color.stone_grey_light,color.stone_grey,color.stone_grey_dark,color.stone_grey_darker)

    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player],wall=wall)
    stair_room_dim = 6

    right_stair_x = map_width//6*5 - stair_room_dim//2
    right_stair_y = map_height//2 - stair_room_dim//2
    right_stair_room = RectangularRoom(right_stair_x,right_stair_y,stair_room_dim,stair_room_dim)

    dungeon.tiles[right_stair_room.inner] = floor
    dungeon.tiles[right_stair_room.center[0]-stair_room_dim//2,right_stair_room.center[1]] = door
    factory.down_staircase.spawn(dungeon,*right_stair_room.center)
    
    engine.player.place(*right_stair_room.center, dungeon)
    
    return dungeon

def deepest_zone(engine: Engine,map_width,map_height): 
    floor = tiles.new_floor(color.earth_light,color.earth_dark)
    wall = tiles.new_wall(color.wood_light,color.wood_dark)
    door = tiles.new_door(color.earth_light,color.wood_light,color.earth_dark,color.wood_dark)
    
    
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player],wall=wall)
    stair_room_dim = 6

    left_stair_x = map_width//6 - stair_room_dim//2
    left_stair_y = map_height//2 - stair_room_dim//2
    left_stair_room = RectangularRoom(left_stair_x,left_stair_y,stair_room_dim,stair_room_dim)

    dungeon.tiles[left_stair_room.inner] = floor
    dungeon.tiles[left_stair_x + stair_room_dim,left_stair_room.center[1]] = door
    factory.up_staircase.spawn(dungeon,*left_stair_room.center)
    engine.player.place(*left_stair_room.center, dungeon)
    return dungeon

def initial_zone(engine: Engine,goingUp,map_width,map_height):
    
    floor = tiles.new_floor(color.earth_light,color.earth_dark)
    wall = tiles.new_wall(color.stone_grey,color.stone_grey_darker)
    door = tiles.new_door(color.earth_light,color.stone_grey,color.earth_dark,color.stone_grey_darker)
    

    dungeon = GameMap(engine, map_width, map_height, entities=[engine.player],wall=wall)

    stair_room_dim = 6

    left_stair_x = map_width//6*3 - stair_room_dim//2
    left_stair_y = map_height//2 - stair_room_dim//2
    left_stair_room = RectangularRoom(left_stair_x,left_stair_y,stair_room_dim,stair_room_dim)

    dungeon.tiles[left_stair_room.inner] = floor
    dungeon.tiles[left_stair_x + stair_room_dim,left_stair_room.center[1]] = door

    right_stair_x = map_width//6*4 - stair_room_dim//2
    right_stair_y = left_stair_y
    right_stair_room = RectangularRoom(right_stair_x,right_stair_y,stair_room_dim,stair_room_dim)

    dungeon.tiles[right_stair_room.inner] = floor
    dungeon.tiles[right_stair_room.center[0]-stair_room_dim//2,right_stair_room.center[1]] = door
    hall_width =right_stair_x- left_stair_x - stair_room_dim
    main_hall = RectangularRoom(left_stair_x + stair_room_dim,left_stair_y+1,hall_width,4)
    dungeon.tiles[main_hall.inner] = floor

    factory.down_staircase.spawn(dungeon,*right_stair_room.center)
    factory.up_staircase.spawn(dungeon,*left_stair_room.center)
    
    factory.invisibility_scroll.spawn(dungeon,*main_hall.center)
    factory.invisibility_scroll.spawn(dungeon,*main_hall.center)
    factory.invisibility_scroll.spawn(dungeon,*main_hall.center)
    factory.invisibility_scroll.spawn(dungeon,*main_hall.center)
    factory.invisibility_scroll.spawn(dungeon,*main_hall.center)

    if goingUp:
        engine.player.place(*right_stair_room.center, dungeon)
    else:
        engine.player.place(*left_stair_room.center, dungeon)
    return dungeon

def generate_level(
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    engine: Engine,
    goingUp: bool,
    level: int 
)-> GameMap:
    """Generate a new dungeon map of the selected floor."""
    
    
    if level == 0:
        return initial_zone(engine,goingUp,map_width,map_height)
    if level == 5:
        return highest_zone(engine,map_width,map_height)
    if level == -5:
        return deepest_zone(engine,map_width,map_height)
    if level > 0:
        floor = tiles.new_floor(color.stone_grey_light,color.stone_grey_dark)
        wall = tiles.new_wall(color.stone_grey,color.stone_grey_darker)
        door = tiles.new_door(color.stone_grey_light,color.stone_grey,color.stone_grey_dark,color.stone_grey_darker)
    else:
        floor = tiles.new_floor(color.earth_light,color.earth_dark)
        wall = tiles.new_wall(color.wood_light,color.wood_dark)
        door = tiles.new_door(color.earth_light,color.wood_light,color.earth_dark,color.wood_dark)
    
    
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player],wall=wall)
    stair_room_dim = 6

    left_stair_x = map_width//6 - stair_room_dim//2
    left_stair_y = map_height//2 - stair_room_dim//2
    left_stair_room = RectangularRoom(left_stair_x,left_stair_y,stair_room_dim,stair_room_dim)

    dungeon.tiles[left_stair_room.inner] = floor
    dungeon.tiles[left_stair_x + stair_room_dim,left_stair_room.center[1]] = door

    right_stair_x = map_width//6*5 - stair_room_dim//2
    right_stair_y = left_stair_y
    right_stair_room = RectangularRoom(right_stair_x,right_stair_y,stair_room_dim,stair_room_dim)

    dungeon.tiles[right_stair_room.inner] = floor
    dungeon.tiles[right_stair_room.center[0]-stair_room_dim//2,right_stair_room.center[1]] = door
    hall_width =right_stair_x- left_stair_x - stair_room_dim
    main_hall = RectangularRoom(left_stair_x + stair_room_dim,left_stair_y+1,hall_width,4)
    dungeon.tiles[main_hall.inner] = floor
    for i in range(abs(level)):
        place_entities(main_hall,dungeon,level) 
    
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
        generate_more_rooms(dungeon,north_placed_rooms,center_candidates,room_min_size,room_max_size,level,floor,door)
        
        #south
        center_candidates =generate_candidate_points(
                                leftmost_x,
                                main_hall.y2 + room_min_size//2,
                                right_stair_x - 1 - room_min_size//2,
                                dungeon.height - room_min_size//2, 
                                n_center_candidates)
        generate_more_rooms(dungeon,south_placed_rooms,center_candidates,room_min_size,room_max_size, level,floor,door)

        
        
    for roomA in north_placed_rooms:
        for roomB in north_placed_rooms:
            if roomA is not roomB:
                door_xy = roomA.touchMiddlePoint(roomB)
                if door_xy is not None:
                    print("connecting adjacent rooms..")
                    dungeon.tiles[door_xy] = door
    
    for roomA in south_placed_rooms:
        for roomB in south_placed_rooms:
            if roomA is not roomB:
                door_xy = roomA.touchMiddlePoint(roomB)
                if door_xy is not None:
                    print("connecting adjacent rooms..")
                    dungeon.tiles[door_xy] = door

    place_equipment(north_placed_rooms + south_placed_rooms,dungeon,level)

    print(len(north_placed_rooms)+len(south_placed_rooms)-2)

    factory.down_staircase.spawn(dungeon,*right_stair_room.center)
    factory.up_staircase.spawn(dungeon,*left_stair_room.center)
    if goingUp:
        player.place(*right_stair_room.center, dungeon)
    else:
        player.place(*left_stair_room.center, dungeon)
    return dungeon

def place_equipment(rooms : list[RectangularRoom],dungeon,level):
    eq_to_place = None
    if level == 4:
        eq_to_place = factory.nice_sword
    elif level == 3:
        eq_to_place = factory.nice_outfit
    elif level == 2:
        eq_to_place = factory.broken_sword
    elif level == 1:
        eq_to_place = factory.worn_outfit
    elif level == 0:
        return
    elif level == -1:
        eq_to_place = factory.amulet_health
    elif level == -2:
        eq_to_place = factory.wooden_staff
    elif level == -3:
        eq_to_place = factory.amulet__great_health
    elif level == -4:
        eq_to_place = factory.nice_staff

    
    if eq_to_place:
        if hasattr(eq_to_place,"parent") and eq_to_place.inInventory:
            return
        room = random.choice(rooms)
        eq_to_place.place(*room.center,dungeon)



def generate_more_rooms(dungeon : GameMap, placed_rooms: list[RectangularRoom],center_candidates : list[Point],room_min_size,room_max_size,level,floor,door):
    
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
        dungeon.tiles[next_room.inner] = floor
        if not next_room.touching(current_room):
            print(f"candidate discarded for not touching")
            continue
        dungeon.tiles[current_room.touchMiddlePoint(next_room)] = door
        print(current_room.touchMiddlePoint(next_room))
        place_entities(next_room,dungeon,level)
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

def place_entities(room: RectangularRoom, dungeon: GameMap, level
) -> None:
    """
    objetos en el suelo siempre:
    arriba: piedras
    abajo: setitas(comida)

    drops random para enemigos:
    rata: comida(no siempre)
    seta: seta(siempre)
    skeleto: scroll simple(no siempre)
    boca: comida(no siempre) diente(se tira)
    wizzo: scroll simple(siempre), scroll guay( a veces)

    """
    debris = None
    if level > 0:
        debris = factory.rock
    if level < 0:
        debris = factory.little_shroom
    if debris:
        for i in range(room.area//100):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            debris.spawn(dungeon,x,y)

    monster_choices = []
    if level == 5:
        pass
    elif level > 2:
        min_monsters = 3
        max_monsters = 10
        monster_choices =random.choices(factory.actorList,weights=factory.A_WeightUp_3_4,k=random.randint(min_monsters, max_monsters))
       
    elif level > 0:
        min_monsters = 1
        max_monsters = 4
        monster_choices =random.choices(factory.actorList,weights=factory.A_WeightUp_1_2,k=random.randint(min_monsters, max_monsters))
        
    elif level == 0:
        pass
    elif level >= -2:
        min_monsters=1
        max_monsters = 4
        monster_choices =random.choices(factory.actorList,weights=factory.A_WeightDown_1_2,k=random.randint(min_monsters, max_monsters))

    elif level > -5:
        min_monsters = 3
        max_monsters = 10
        monster_choices =random.choices(factory.actorList,weights=factory.A_WeightDown_3_4,k=random.randint(min_monsters, max_monsters))

    else:# level == -10
        pass

    for m in monster_choices:
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)
        m.spawn(dungeon,x,y)

    
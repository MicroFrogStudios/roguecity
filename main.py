import tcod

from map.game_map import GameMap
import typing
import factories.entity_factories as factory
from engine import Engine
from map.gen.dungeon import generate_dungeon
import copy
import enums.color as color
import traceback

def main():
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 2
    max_items_per_room = 2
   


    tileset = tcod.tileset.load_tilesheet(
        "tilesets/basic.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )


    player = copy.deepcopy(factory.player)
    engine = Engine(player=player)
    engine.game_map = generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        engine=engine,
        max_monsters_per_room=max_monsters_per_room,
        max_items_per_room=max_items_per_room
    )

    engine.update_fov()
    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon!", color.welcome_text
    )
    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="Rogue City project",
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(screen_width, screen_height, order="F")
        while True:
            root_console.clear()
            engine.event_handler.on_render(console=root_console)
            context.present(root_console)
            engine.render(console=root_console)

            try:
                for event in tcod.event.wait():
                    context.convert_event(event)
                    engine.event_handler.handle_events(event)
            except Exception:  # Handle exceptions in game.
                traceback.print_exc()  # Print error to stderr.
                # Then print the error to the message log.
                engine.message_log.add_message(traceback.format_exc(), color.error)
            
            


if __name__ == "__main__":
    main()
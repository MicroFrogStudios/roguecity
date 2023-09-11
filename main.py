import tcod

from map.game_map import GameMap
from inputHandlers import EventHandler
from classes.entity import Entity
from engine import Engine

def main():
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 45

    tileset = tcod.tileset.load_tilesheet(
        "tilesets/basic.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    event_handler = EventHandler()

    player = Entity(int(screen_width / 2), int(screen_height / 2), "@", (255, 255, 255))
    npc = Entity(int(screen_width / 2 - 5), int(screen_height / 2), "A", (255, 255, 0))
    entities = {npc, player}

    game_map = GameMap(map_width, map_height)

    engine = Engine(entities=entities,event_handler=event_handler,player=player,game_map=game_map)

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="Rogue City project",
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(screen_width, screen_height, order="F")
        while True:
            engine.render(console=root_console,context=context)
            events = tcod.event.wait()
            engine.handle_events(events)
            


if __name__ == "__main__":
    main()
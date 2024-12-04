"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy
from typing import Optional
import lzma
import pickle
import traceback

import tcod
from tcod import libtcodpy
import config
import enums.color as color
from engine import Engine
import factories.entity_factory as entity_factory
import handlers.input_handlers as input_handlers

from map.game_map import GameWorld


# Load the background image and remove the alpha channel.
background_image = tcod.image.load("assets/sprites/background.png")[:, :, :3]


def new_game() -> Engine:
    """Return a brand new game session as an Engine instance."""
    
    # Map dimensions, cant be smaller than camera/console sizes
    map_width = 200
    map_height = 200

    room_max_size = 30
    room_min_size = 6
    max_rooms = 30

    max_monsters_per_room = 2
    max_items_per_room = 2

    player = copy.deepcopy(entity_factory.player)

    engine = Engine(player=player)

    engine.game_world = GameWorld(
        engine=engine,
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        max_monsters_per_room=max_monsters_per_room,
        max_items_per_room=max_items_per_room,
    )
    
    engine.game_world.generate_floor()
    engine.update_fov()    
    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon!", color.welcome_text
    )
    return engine

def test_game() -> Engine:
    map_width = 200
    map_height = 200
    player = copy.deepcopy(entity_factory.player)
    engine = Engine(player=player)

    engine.game_world = GameWorld(
        engine=engine,
        map_width=map_width,
        map_height=map_height,
    )
    engine.game_world.tutorial_map()
    engine.update_fov()    
    engine.message_log.add_message(
        "Hello and welcome, to the test chamber", color.welcome_text
    )
    return engine


def load_game(filename: str) -> Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine

class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""
    def __init__(self):
        from interface.navigable_menu import OptionsMenu, Container
        self.engine = Engine(None)
        self.engine.game_world = GameWorld(engine=self.engine,map_height=200,map_width=200)
        self.menu = OptionsMenu("Start Menu",[
            ("Start a new Game",lambda: input_handlers.MainGameEventHandler(new_game())),
            ("Continue game",self.tryContinue),
            ("Exit", lambda:self.ev_quit(None))
        ])
        

    def on_render(self, console: tcod.console.Console) -> None:
        """Render the main menu on a background image."""
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "CRAWLING UNDER THE MOUNTAIN",
            fg=color.menu_title,
            alignment=libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By Microfrog dev",
            fg=color.menu_title,
            alignment=libtcodpy.CENTER,
        )

        menu_width = 20
        self.menu.width = menu_width
        self.menu.height = 11
        self.menu.x = console.width // 2 
        self.menu.y = console.height // 2 - 2
        
        self.menu.render(console,self.engine)
        # for i, text in enumerate(
        #     ["[N] Play a new game", "[C] Continue last game", "[Q] Quit"]
        # ):
        #     console.print(
        #         console.width // 2,
        #         console.height // 2 - 2 + i,
        #         text.ljust(menu_width),
        #         fg=color.menu_text,
        #         bg=color.black,
        #         alignment=libtcodpy.CENTER,
        #         bg_blend=libtcodpy.BKGND_ALPHA(64),
        #     )

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        
        key = event.sym
        # if event.sym in (tcod.event.KeySym.q, tcod.event.KeySym.ESCAPE):
        #     raise SystemExit()
        # elif event.sym == tcod.event.KeySym.c:
        #     try:
        #         return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
        #     except FileNotFoundError:
        #         return input_handlers.PopupMessage(self, "No saved game to load.")
        #     except Exception as exc:
        #         traceback.print_exc()  # Print to stderr.
        #         return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        # elif event.sym == tcod.event.KeySym.n:
        #     return input_handlers.MainGameEventHandler(new_game())
        if event.sym == tcod.event.KeySym.t:
            return input_handlers.MainGameEventHandler(test_game())
        
        if key in config.MOVE_KEYS:
            dx, dy = config.MOVE_KEYS[key]
            self.menu.navigate(dx,dy)  
        elif key in config.CONFIRM_KEYS:
            return self.menu.on_confirm()
        return None
    
    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        super().ev_mousemotion(event)
        for cursor, button in self.menu.menu_buttons():
             if button.hovering(self.engine):
                 self.menu.set_cursor(*cursor)
                 return
    
    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[input_handlers.BaseEventHandler]:
        """By default any mouse click exits this input handler."""

        """Left click confirms a selection."""
        
        for c, b in self.menu.menu_buttons():
            if b.hovering(self.engine) and event.button == 1:
                return self.menu.on_confirm()
    
    def tryContinue(self):
        try:
            return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
        except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game to load.")
        except Exception as exc:
                traceback.print_exc()  # Print to stderr.
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
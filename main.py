import time
from typing import Optional
import tcod

from components.ai import PlayerAI
import config

import setup


import copy
import enums.color as color
import traceback
import exceptions
import handlers.input_handlers as input_handlers

def main():

    tileset_basic = tcod.tileset.load_tilesheet(
        "tilesets/basic.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    tileset = tcod.tileset.load_tilesheet(
        "tilesets/curses_640x300.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )

    # tileset = tcod.tileset.load_tilesheet(
    #     "tilesets/curses_square_16x16.png", 16, 16, tcod.tileset.CHARMAP_CP437
    # )
    

    
    FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED
    
    while True:
        handler: input_handlers.BaseEventHandler = setup.MainMenu()

        with tcod.context.new(

            tileset=tileset,
            title="Rogue City project",
            vsync=True,
            sdl_window_flags=FLAGS
        ) as context:
            root_console = tcod.console.Console(config.screen_width, config.screen_height, order="F")
            try:
                while True:
                    root_console.clear()
                    handler.on_render(console=root_console)
                    context.present(root_console,keep_aspect=True, integer_scaling=True)
                    
                    try:
                        
                        for event in tcod.event.get():
                            context.convert_event(event)
                            handler = handler.handle_events(event)
                        if hasattr(handler, "player_controller"):
                            handler.handle_player_tasks()
                        
                    except Exception:  # Handle exceptions in game.
                        traceback.print_exc()  # Print error to stderr.
                        # Then print the error to the message log.
                        if isinstance(handler, input_handlers.EventHandler):
                            handler.engine.message_log.add_message(
                                traceback.format_exc(), color.error
                            )
            except exceptions.QuitWithoutSaving:
                continue
            except SystemExit:  # Save and quit.
                save_game(handler, "savegame.sav")
                raise
            except BaseException:  # Save on any other unexpected exception.
                save_game(handler, "savegame.sav")
                raise


def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active Engine then save it."""
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game saved.")


if __name__ == "__main__":
    main()
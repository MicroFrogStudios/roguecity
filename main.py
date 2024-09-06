import tcod

import config
import setup


import copy
import enums.color as color
import traceback
import exceptions
import inputHandlers

def main():
    screen_width = 120
    screen_height = 50


    tileset_basic = tcod.tileset.load_tilesheet(
        "tilesets/basic.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    tileset = tcod.tileset.load_tilesheet(
        "tilesets/curses_640x300.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )

    # tileset = tcod.tileset.load_tilesheet(
    #     "tilesets/curses_square_16x16.png", 16, 16, tcod.tileset.CHARMAP_CP437
    # )
    

    

    handler: inputHandlers.BaseEventHandler = setup.MainMenu()

    with tcod.context.new(

        tileset=tileset,
        title="Rogue City project",
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(config.screen_width, config.screen_height, order="F")
        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(root_console,keep_aspect=True, integer_scaling=True)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()  # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, inputHandlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # Save and quit.
            save_game(handler, "savegame.sav")
            raise
        except BaseException:  # Save on any other unexpected exception.
            save_game(handler, "savegame.sav")
            raise


def save_game(handler: inputHandlers.BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active Engine then save it."""
    if isinstance(handler, inputHandlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game saved.")


if __name__ == "__main__":
    main()
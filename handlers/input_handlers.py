from __future__ import annotations

import os
import time
from typing import Callable, Optional, TYPE_CHECKING, Tuple, Union

from tcod.console import Console
import tcod.event
import tcod.libtcodpy

import actions
from actions import (
    Action,
    BumpAction,
    WaitAction,
    
)


from components.ai import  PlayerInteract, PlayerPathing
import config
import enums.color as color
import exceptions
from interface.navigable_menu import Container, InventoryMenu, TabContainer
from interface.panels import MapContextPanel
from player_controller import PlayerController

if TYPE_CHECKING:
    from engine import Engine
    from classes.item import Item
    from classes.entity import Entity
    
MOVE_KEYS = config.MOVE_KEYS

WAIT_KEYS = config.WAIT_KEYS

CONFIRM_KEYS = config.CONFIRM_KEYS

ActionOrHandler = Union[Action, "BaseEventHandler"]
"""An event handler return value which can trigger an action or switch active handlers.

If a handler is returned then it will become the active handler for future events.
If an action is returned it will be attempted and if it's valid then
MainGameEventHandler will become the active handler.
"""

class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle an event and return the next active event handler."""
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} can not handle actions."
        return self

    def on_render(self, console: tcod.console.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[ActionOrHandler]:
        raise SystemExit()

class PopupMessage(BaseEventHandler):
    """Display a popup text window."""

    def __init__(self, parent_handler: BaseEventHandler, text: str):
        self.parent = parent_handler
        self.text = text

    def on_render(self, console: tcod.console.Console) -> None:
        """Render the parent and dim the result, then print the message on top."""
        self.parent.on_render(console)
        console.tiles_rgb["fg"] //= 8
        console.tiles_rgb["bg"] //= 8

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg=color.white,
            bg=color.black,
            alignment=tcod.CENTER,
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[BaseEventHandler]:
        """Any key returns to the parent handler."""
        return self.parent

class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine
        self.player_controller = PlayerController.get_instance(self.engine.player)

    def handle_player_tasks(self):
        if self.player_controller.current_task is None:
            if self.player_controller.hasNext():
                self.player_controller.current_task = self.player_controller.next()
        elif self.player_controller.current_task.finished():
            self.player_controller.current_task = None
        else:
            self.handle_action(self.player_controller.current_task) 
            time.sleep(0.04)       
        return

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine."""
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            # A valid action was performed.
            if not self.engine.player.is_alive:
                # The player was killed sometime during or after the action.
                return GameOverEventHandler(self.engine)
            
            return MainGameEventHandler(self.engine)  # Return to the main handler.
        return self

    def handle_action(self, action: Optional[Action]) -> bool:
        """Handle actions returned from event methods.

        Returns True if the action will advance a turn.
        """
        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False  # Skip enemy turn on exceptions.

        self.engine.handle_enemy_turns()

        self.engine.update_fov()
        return True

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        (x,y) = self.engine.camera_to_map_coordinates(event.tile.x, event.tile.y)
        if self.engine.game_map.in_bounds(x, y) and self.engine.in_camera_view(x,y):
            self.engine.mouse_location = x, y

    def on_render(self, console: tcod.console.Console) -> None:
        
        self.engine.render(console)





class MainGameEventHandler(EventHandler):
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        action: Optional[Action] = None
        self.player_controller.interrupt()
        key = event.sym
        modifier = event.mod
        player = self.engine.player

        if key == tcod.event.KeySym.PERIOD and modifier & (
            tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT
        ):
            return actions.TakeStairsAction(player)
        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)

        elif key == tcod.event.KeySym.i: # hot key to big menu
            return TabMenuHandler(self.engine,1)
        elif key == tcod.event.KeySym.q:
            contextEntity = self.engine.game_map.closest_visible_entity()
            if contextEntity:
                MapContextPanel.set_entities([contextEntity],self.engine)
                return SelectedEntityHandler(self.engine,[contextEntity])
            self.engine.message_log.add_message("You see nothing interesting",color.impossible)
        
        elif key == tcod.event.KeySym.l: # keep for accesibility
            return LookHandler(self.engine)
        elif key == tcod.event.KeySym.ESCAPE: # big menu instead of instquit
            return TabMenuHandler(self.engine)
            # raise SystemExit()
        # elif key == tcod.event.KeySym.c:# showed left bottom
        #     return CharacterScreenEventHandler(self.engine)
        elif key == tcod.event.KeySym.v:# hot key to big menu
            return TabMenuHandler(self.engine,2)

        # No valid key was pressed
        return action
    
    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        """By default any mouse click exits this input handler."""

        """Left click confirms a selection."""
        entities = self.engine.check_visible_entities_on_mouse()
        
        if entities and event.button == 1:
            return SelectedEntityHandler(self.engine,entities)
        elif event.button == 3:
            x,y = self.engine.camera_to_map_coordinates(event.tile.x, event.tile.y)
            if self.engine.game_map.explored[x,y] and self.engine.game_map.tiles[x,y]['walkable']:
                if entities:
                    for e in entities:
                        self.engine.player.ai = PlayerInteract(self.engine.player,e)
                        self.player_controller.aiList.append(self.engine.player.ai)
                else:
                    self.engine.player.ai = PlayerPathing(self.engine.player, (x,y))
                    self.player_controller.aiList.append(self.engine.player.ai)
            
        
        
        return super().ev_mousebuttondown(event)
    
    def on_render(self, console: Console) -> None:

        super().on_render(console)
        
        MapContextPanel.render(console=console, engine=self.engine)
         


class GameOverEventHandler(EventHandler):

    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")  # Deletes the active save file.
        raise exceptions.QuitWithoutSaving()  # Avoid saving a finished game.

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.KeySym.ESCAPE:
            self.on_quit()
    
CURSOR_Y_KEYS = {
    tcod.event.KeySym.UP: -1,
    tcod.event.KeySym.DOWN: 1,
    tcod.event.KeySym.PAGEUP: -10,
    tcod.event.KeySym.PAGEDOWN: 10,
}

@DeprecationWarning
class HistoryViewerOld(EventHandler):
    """Print the history on a larger window which can be navigated."""

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)  # Draw the main state as the background.

        log_console = tcod.console.Console(console.width - 6, console.height - 6)

        # Draw a frame with a custom banner title.
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "┤Message history├", alignment=tcod.libtcodpy.CENTER
        )

        # Render the message log using the cursor parameter.
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        # Fancy conditional movement to make it feel right.
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.KeySym.HOME:
            self.cursor = 0  # Move directly to the top message.
        elif event.sym == tcod.event.KeySym.END:
            self.cursor = self.log_length - 1  # Move directly to the last message.
        else:  # Any other key moves back to the main game state.
            return MainGameEventHandler(self.engine)
        return None


class AskUserEventHandler(EventHandler):
    """Handles user input for actions which require special input."""


    def  ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """By default any key exits this input handler."""
        if event.sym in {  # Ignore modifier keys.
            tcod.event.KeySym.LSHIFT,
            tcod.event.KeySym.RSHIFT,
            tcod.event.KeySym.LCTRL,
            tcod.event.KeySym.RCTRL,
            tcod.event.KeySym.LALT,
            tcod.event.KeySym.RALT,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        """By default any mouse click exits this input handler."""
        return self.on_exit()

    def on_exit(self) -> Optional[ActionOrHandler]:
        """Called when the user is trying to exit or cancel an action.

        By default this returns to the main event handler.
        """
        return MainGameEventHandler(self.engine)

class SelectedEntityHandler(AskUserEventHandler):
    
    def __init__(self, engine: actions.Engine,entities : list[Entity]):
        super().__init__(engine)
        MapContextPanel.entities = entities
        
    
    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        super().ev_mousemotion(event)
        for cursor, button in MapContextPanel.container.menu_buttons():
             if button.hovering(self.engine):
                 MapContextPanel.container.current_tab.has_focus=True
                 MapContextPanel.container.set_cursor(*cursor)
                 print("hovering")
                 return
    
    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        """By default any mouse click exits this input handler."""
        
        for c, b in MapContextPanel.container.menu_buttons():
            if b.hovering(self.engine) and event.button == 1:
                return MapContextPanel.container.on_confirm()
            if event.button == 3:
                return super().ev_mousebuttondown(event)
    
    def on_render(self, console: Console) -> None:

        super().on_render(console)
        
        MapContextPanel.render(console=console, engine=self.engine,selected=True)
         
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """By default any key exits this input handler."""
        if event.sym in {  # Ignore modifier keys.
            tcod.event.KeySym.LSHIFT,
            tcod.event.KeySym.RSHIFT,
            tcod.event.KeySym.LCTRL,
            tcod.event.KeySym.RCTRL,
            tcod.event.KeySym.LALT,
            tcod.event.KeySym.RALT,
        }:
            return None
        
        key = event.sym
        if key == tcod.event.KeySym.ESCAPE or key == tcod.event.KeySym.q:
            return MainGameEventHandler(self.engine)
        elif key in MOVE_KEYS:
            MapContextPanel.container.current_tab.has_focus=True
            dx, dy = MOVE_KEYS[key]
            MapContextPanel.container.navigate(dx,dy)
        elif key in CONFIRM_KEYS:
            return MapContextPanel.container.on_confirm()
        elif key == tcod.event.KeySym.TAB:
            MapContextPanel.container.navigate(0,0,1)
        
        elif key == tcod.event.KeySym.g:
            if hasattr(MapContextPanel.entities[MapContextPanel.container.tab_cursor],"pickUpInteractable"):
                item :Item = MapContextPanel.entities[MapContextPanel.container.tab_cursor]
                from components.interactable_component import PickUpInteractable 
                if item.pickUpInteractable.check_player_activable():
                    self.engine.entities = None
                    return item.pickUpInteractable.get_action(self.engine.player.interactor)
            
            
        
        
    
    

class NavigableMenuHandler(AskUserEventHandler):
    """This might not be used ever"""
    def __init__(self, engine: actions.Engine,rootMenu :Container):
        super().__init__(engine)
        self.rootMenu = rootMenu

    def on_render(self, console: Console) -> None:
        super().on_render(console)
        self.rootMenu.render(console,self.engine)
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Action | BaseEventHandler | None:
        key = event.sym
        if key == tcod.event.KeySym.ESCAPE: # go back
            return MainGameEventHandler(self.engine)
        elif key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            self.rootMenu.navigate(dx,dy)
            
        elif key in CONFIRM_KEYS:
            return self.rootMenu.on_confirm()

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        super().ev_mousemotion(event)
        for cursor, button in self.rootMenu.menu_buttons():
             if button.hovering(self.engine):
                 self.rootMenu.set_cursor(*cursor)
                 return




class TabMenuHandler(AskUserEventHandler):
    "Handler that shows menu interface and switches controls to menu navigation"
        
    def __init__(self, engine: actions.Engine,cursor = 0):
        super().__init__(engine)
        inventoryMenu = InventoryMenu(engine.player.inventory)
        from interface.navigable_menu import OptionsMenu, HistoryViewer
        optionsTab = OptionsMenu("OPTIONS",[("Continue",lambda: MainGameEventHandler(self.engine)),
                                            ("Controls",lambda: ControlListHandler(self.engine)),
                                            ("Save and exit",lambda: self.ev_quit(None))
                                            ])
        logTab = HistoryViewer("LOG",engine,x=0,y=0,width=80,height=40)
        self.rootMenu = TabContainer(tabs=[optionsTab,inventoryMenu,logTab],x=0,y=0,width=80,height=40,tab_cursor=cursor)
        
    def on_render(self, console: Console) -> None:
        super().on_render(console)
        self.rootMenu.render(console,self.engine)
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        key = event.sym
        if key == tcod.event.KeySym.ESCAPE: # big menu instead of instquit
            return MainGameEventHandler(self.engine)
        elif key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            self.rootMenu.navigate(dx,dy)
            
        elif key in CONFIRM_KEYS:
            return self.rootMenu.on_confirm()
        elif key == tcod.event.KeySym.TAB:
            self.rootMenu.navigate(0,0,1)
            
        # super().ev_keydown(event)
        
    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        """By default any mouse click exits this input handler."""

        """Left click confirms a selection."""
        
        for c, b in self.rootMenu.current_tab.menu_buttons():
            if b.hovering(self.engine) and event.button == 1:
                return self.rootMenu.on_confirm()
            if event.button == 3:
                return super().ev_mousebuttondown(event)
        
        for b in self.rootMenu.tabButtons:
            if b.hovering(self.engine) and event.button == 1:
                b.on_click()
    
    def ev_mousewheel(self, event: tcod.event.MouseWheel) -> Action | BaseEventHandler | None:
        self.rootMenu.navigate(0,-event.y)
        
        return super().ev_mousewheel(event)
    
    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        super().ev_mousemotion(event)
        for cursor, button in self.rootMenu.current_tab.menu_buttons():
             if button.hovering(self.engine):
                 self.rootMenu.current_tab.set_cursor(*cursor)
                 return
 
 
   
class InventoryEventHandler(AskUserEventHandler):
    """This handler lets the user select an item.

    What happens then depends on the subclass.
    """
    
    TITLE = "<missing title>"

    def on_render(self, console: tcod.console.Console) -> None:
        """Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        Will move to a different position based on where the player is located, so the player can always see where
        they are.
        """
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        height = number_of_items_in_inventory + 2

        if height <= 3:
            height = 3

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                console.print(x + 1, y + i + 1, f"({item_key}) {item.name}")
        else:
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Called when the user selects a valid item."""
        raise NotImplementedError()


class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""

    def __init__(self, engine: Engine, range : int = 99):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y
        self.range = range

    def on_render(self, console: tcod.console.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        x, y = self.engine.mouse_location
        x, y = self.engine.map_to_camera_coordinates(x,y)

        console.rgb["bg"][x, y] = color.white
        console.rgb["fg"][x, y] = color.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """Check for key movement or confirmation keys."""
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1  # Holding modifier keys will speed up key movement.
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            px = self.engine.player.x
            py = self.engine.player.y
            # Clamp the cursor index to the map size.
            x = max(self.engine.x_left_ref, min(x, self.engine.x_right_ref - 1,px+self.range),px-self.range)
            y = max(self.engine.y_left_ref, min(y, self.engine.y_right_ref - 1,py+self.range),py-self.range)
            self.engine.mouse_location = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        """Left click confirms a selection."""
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
               return self.on_index_selected(*self.engine.camera_to_map_coordinates(*event.tile))
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        """Called when an index is selected."""
        raise NotImplementedError()


class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard."""

    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        """Return to main handler."""
        return MainGameEventHandler(self.engine)
    
    def on_render(self, console: Console) -> None:
        super().on_render(console)
        
        MapContextPanel.render(console=console, engine=self.engine)


class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a single enemy. Only the enemy selected will be affected."""

    def __init__(
        self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__(engine)

        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""

    def __init__(
        self,
        engine: Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.console.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        x, y = self.engine.mouse_location
        x, y = self.engine.map_to_camera_coordinates(x,y)
        # Draw a rectangle around the targeted area, so the player can see the affected tiles.
        console.draw_frame(
            x=x - self.radius - 1,
            y=y - self.radius - 1,
            width=self.radius ** 2,
            height=self.radius ** 2,
            fg=color.red,
            clear=False,
        )

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        return self.callback((x, y))


class ControlListHandler(AskUserEventHandler):
    TITLE = "Controls Info"   
    
    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)

        
        x = 0

        y = 0

        width = len(self.TITLE) + 30

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=25,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(
            x=x + 1, y=y + 2, string="Bump into enemies to attack them"
        )
        
        console.print(
            x=x + 1, y=y + 4, string="left mouse click on objects to see info"
        )
        
        console.print(
            x=x + 1, y=y + 6, string="Move/Navigate: WASD, numpad or arrows"
        )
        console.print(
            x=x + 1, y=y + 8, string="Move/interact also with mouse right click"
        )
        console.print(
            x=x + 1, y=y + 10, string="Context menu: 'Q'"
        )
        
        console.print(
            x=x + 1, y=y + 12, string="Confirm: 'E' or RETURN or INTRO"
        )
        console.print(
            x=x + 1, y=y + 14, string="Menu: 'ESC'"
        )
        console.print(
            x=x + 1, y=y + 16, string="Inventory: 'I'"  
        )
        console.print(
            x=x + 1, y=y + 18, string="Message log: 'V'"  
        )
        console.print(
            x=x + 1, y=y + 20, string="Next tab: TAB"  
        )
            
class CharacterScreenEventHandler(AskUserEventHandler):
    TITLE = "Character Information"

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=7,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(
            x=x + 1, y=y + 4, string=f"Attack: {self.engine.player.fighter.power} + ({self.engine.player.fighter.power_bonus})"
        )
        console.print(
            x=x + 1, y=y + 5, string=f"Defense: {self.engine.player.fighter.defense} + ({self.engine.player.fighter.defense_bonus})"
        )
from typing import TYPE_CHECKING

from tcod.console import Console

from components.inventory_component import Inventory
from engine import Engine



if TYPE_CHECKING:
    from tcod.console import Console
    from engine import Engine
    from interface.button import Button





class TabContainer:
    def __init__(self,tabs) -> None:
        
        self.tabs: list[BaseMenu] = tabs
        self.tab_cursor = 0



class BaseMenu:
    parent : TabContainer
    def __init__(self, submenus,parent ) -> None:
        self.submenus : list[SubMenu] = submenus
        self.submenu_cursor : int = 0
        self.parent = parent
        

    def render(self,console: Console, engine: Engine) -> None:
        for sub in self.submenus:
            sub.render(console,engine)


class InventoryMenu(BaseMenu):
    
    
    def __init__(self, inventory : Inventory) -> None:
        self.inventory = inventory
        submenus = [SingleOptionSubMenu( button= Button()) for item in self.inventory.items]
        super().__init__(submenus)
    
    def render(self, console: Console, engine: Engine) -> None:
        for i, sub in enumerate(self.submenus):
            if i == self.submenu_cursor:                
                sub.render(console,engine,highlight=True)
                selected = sub
            

## menus contains submenus, submenus can be
#  an entity with their interactables(that can be clicked or navigated)
#  or a single column with only info
#  or an setting that can be changed clicking buttons

# might need to tell submenus form menu their root position so it nows where to move everything in it

class SubMenu:
    parent : BaseMenu
    def render(self,console: Console, engine: Engine, highlight = False) -> None:
        raise NotImplementedError()

class SingleOptionSubMenu(SubMenu):

    def __init__(self, button : Button) -> None:
        self.button = button

    def render(self,console: Console, engine: Engine) -> None:
        self.button.render(console,engine)
        
        

class MultiOptionSubMenu(SubMenu):

    def __init__(self,title , buttons: list[Button]) -> None:
        self.title = title
        self.buttons = buttons
        
    def render(self,console: Console, engine: Engine) -> None:
        for b in self.buttons:
            b.render(console,engine) # ¿?
            

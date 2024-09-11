from typing import TYPE_CHECKING



if TYPE_CHECKING:
    from tcod.console import Console
    from engine import Engine
    from interface.button import Button

class Tab:
    
    def __init__(self,name, menu) -> None:
        self.name=name
        self.menu=menu



class TabContainer:
    tabs: list[Tab]


class BaseMenu:
    
    def __init__(self, submenus) -> None:
        self.submenus : list[SubMenu] = submenus
        self.submenu_cursor : int = 0

    def render(self,console: Console, engine: Engine) -> None:
        for sub in self.submenus:
            sub.render(console,engine)
    


## menus contains submenus, submenus can be
#  an entity with their interactables(that can be clicked or navigated)
#  or a single column with only info
#  or an setting that can be changed clicking buttons

# might need to tell submenus form menu their root position so it nows where to move everything in it

class SubMenu:

    def render(self,console: Console, engine: Engine) -> None:
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

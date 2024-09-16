from __future__ import annotations
from typing import TYPE_CHECKING

from tcod.console import Console

from components.inventory_component import Inventory
from engine import Engine
import config
from enums import color
from interface.button import Button

if TYPE_CHECKING:
    from tcod.console import Console
    from engine import Engine
    




class TabContainer:
    def __init__(self,tabs, x = 0, y = 0, width = config.screen_width ,height = config.screen_height) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tabs: list[BaseMenu] = tabs
        for tab in self.tabs:
            tab.parent = self
        self.tab_cursor = 0
        
    def render(self,console: Console, engine: Engine):
        console.draw_frame(self.x,self.y,self.width,self.height,clear=True)
        for i, tab in enumerate(self.tabs):
            console.draw_frame(x=self.x+ i*7,y = self.y,height=3,width=7)
            console.print(x=self.x+ i*7,y = self.y+1,string=tab.name)
            if i == self.tab_cursor:
              console.print(x=self.x+ i*7,y = self.y+1,string=tab.name,fg=color.button_color)
              tab.render(console,engine)
              



class BaseMenu:
    parent : TabContainer
    def __init__(self, submenus, name) -> None:
        self.submenus : list[SubMenu] = submenus
        self.scroll_offset = 0
        self.submenu_cursor : int = 0
        self.name = name
        
        

    def render(self,console: Console, engine: Engine) -> None:
        for sub in self.submenus:
            sub.render(console,engine)


class InventoryMenu(BaseMenu):
    """ Menu displaying an inventory"""
    
    def __init__(self, inventory : Inventory) -> None:
        self.inventory = inventory
        submenus = [MultiOptionSubMenu( item.name,[i.name for i in item.interactables],[i.get_action for i in item.interactables]) for item in self.inventory.items]
        for sub in submenus:
            sub.parent = self
        super().__init__(submenus, "INVTORY")
        
    
    def render(self, console: Console, engine: Engine) -> None:
        for i, sub in enumerate(self.submenus):              
            sub.render(console,engine,selected=i == self.submenu_cursor)
                
            

## menus contains submenus, submenus can be
#  an entity with their interactables(that can be clicked or navigated)
#  or a single column with only info
#  or an setting that can be changed clicking buttons

# might need to tell submenus form menu their root position so it nows where to move everything in it

class SubMenu:
    parent : BaseMenu
    def render(self,console: Console, engine: Engine, selected = False) -> None:
        raise NotImplementedError()

class SingleOptionSubMenu(SubMenu):

    def __init__(self,parent : BaseMenu, content : str, onSelected :function) -> None:
        self.parent = parent
        self.button = Button(0,0,content)
        self.onSelected = onSelected

    def render(self,console: Console, engine: Engine) -> None:
        self.button.render(console,engine)
        
        

class MultiOptionSubMenu(SubMenu):

    def __init__(self,title , optionList : list, onSelectedList:list) -> None:
        self.title = title
        self.buttons = [ Button(0,0,title,on_click=on_click)for title,on_click in zip(optionList,onSelectedList) ]
        
    def render(self,console: Console, engine: Engine,selected) -> None:
        for b in self.buttons:
            b.render(console,engine) # ¿?
            

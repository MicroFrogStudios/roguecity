from __future__ import annotations
from typing import TYPE_CHECKING

from tcod.console import Console


from components.inventory_component import Inventory
from engine import Engine
import config
from enums import color
from interface.button import Button
from tcod import libtcodpy
from interface.panels import InventoryContextPanel

if TYPE_CHECKING:
    from tcod.console import Console
    from engine import Engine
    from classes.entity import Entity
    


class Container:
    def __init__(self, x = 0, y = 0, width = config.screen_width ,height = config.screen_height) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def render(self,console: Console, engine:Engine):
        raise NotImplementedError()
    
    def on_confirm(self):
        NotImplementedError()
    


class SimpleContainer(Container):
    def __init__(self,menu, x=0, y=0, width=config.screen_width, height=config.screen_height) -> None:
        super().__init__(x, y, width, height)
        self.menu=menu
        
    def render(self, console: Console, engine: Engine):
        console.draw_frame(self.x,self.y,self.width,self.height,bg=color.black,clear=True)

class TabContainer(Container):
    def __init__(self,tabs, x = 0, y = 0, width = config.screen_width ,height = config.screen_height) -> None:
        super().__init__(x,y,width,height)
        self.tabs: list[BaseMenu] = tabs
        for tab in self.tabs:
            tab.parent = self
        self.tab_cursor = 0
        
    def render(self,console: Console, engine: Engine):
        console.draw_frame(self.x,self.y,self.width,self.height,bg=color.black,clear=True)
        width_acc = 0
        for i, tab in enumerate(self.tabs):
            
            tab_width = len(tab.name)+2
            if i == self.tab_cursor:
                console.draw_frame(x=self.x+ width_acc,y = self.y,height=3,width=tab_width,decoration="┌─┐│ ││ │")
                console.print(x=self.x+ width_acc+tab_width//2,y = self.y+1,string=tab.name,fg=color.button_text,alignment=libtcodpy.CENTER)
                tab.render(console,engine)
            else:
                console.draw_frame(x=self.x+ width_acc,y = self.y,height=3,width=tab_width)
                console.print(x=self.x+ width_acc+tab_width//2,y = self.y+1,string=tab.name,alignment=libtcodpy.CENTER)
            
              
            width_acc += tab_width
              
    def navigate(self,dx,dy,dz=0):
        self.current_tab.navigate(dx,dy)
        self.tab_cursor += dz
        self.tab_cursor %= len(self.tabs)
    def on_confirm(self):
        return self.current_tab.on_confirm()
    
    @property          
    def current_tab(self):
        return self.tabs[self.tab_cursor]



class BaseMenu:
    parent : Container
    def __init__(self, submenus, name,padding = 0, submenu_height=1) -> None:
        self.submenus : list[SubMenu] = submenus
        self.submenu_cursor : int = 0
        self.name = name
        self.padding = padding
        self.submenu_height = submenu_height
        
    def navigate(self,dx,dy):
        self.submenu_cursor += dy
        self.submenu_cursor %= len(self.submenus) 
    
    def set_cursor(self,x,y):
        self.submenu_cursor = y
        

    def menu_buttons(self)-> list[tuple[tuple[int,int],Button]]:
        raise NotImplementedError()
    
    @property
    def submenus_visible(self):
        return self.submenus[self.current_page*self.page_size:(self.current_page + 1)*self.page_size]
    
    @property
    def page_size(self):
        return (self.parent.height-4)//self.submenu_height
        
    @property
    def current_page(self):
        return self.submenu_cursor//self.page_size
        
    
    def render(self,console: Console, engine: Engine) -> None:
        for sub in self.submenus_visible:
            sub.render(console,engine)
            
    def on_confirm(self):
        """ performs the effects of clicking on the current selection of the menu"""
        raise NotImplementedError()

class StatusMenu(BaseMenu):
    def __init__(self, entity :Entity, name) -> None:
        submenus = entity.description
        super().__init__(submenus, name)


class InventoryMenu(BaseMenu):
    """ Menu displaying an inventory"""
    
    def __init__(self, inventory : Inventory) -> None:
        self.inventory = inventory
        submenus = [MultiOptionSubMenu( item.name,
                                       [i.name for i in item.get_interactables()],
                                       [lambda i = inter: i.get_action(inventory.parent.interactor) for inter in item.get_interactables()])
                    for item in self.inventory.items]
        for sub in submenus:
            sub.parent = self
        super().__init__(submenus, "INVENTORY",padding=3,submenu_height=4)
        
    def navigate(self, dx, dy):
        super().navigate(dx, dy)
        self.submenus[self.submenu_cursor].navigate(dx)
        
    def set_cursor(self, x, y):
        super().set_cursor(x, y)
        self.submenus[self.submenu_cursor].set_cursor(x)
    
    def menu_buttons(self) -> list[tuple[tuple[int,int],Button]]:
        flat_map = lambda f, outer_list: (y for inner_list in  outer_list for y in f(inner_list))
        return flat_map(lambda x: zip(
            [(y,self.submenus.index(x)) for y in range(len(x.buttons))],
            x.buttons),self.submenus_visible)

        
    def render(self, console: Console, engine: Engine) -> None:
        for i, sub in enumerate(self.submenus_visible):
            
            x = self.parent.x + self.padding
            y = self.parent.y + 4 + self.submenu_height*i
            width = self.parent.width - self.padding*2
            height = self.submenu_height
            
            sub.reposition(x,y,width,height)
            sub.render(console,engine,selected=i + self.page_size*self.current_page == self.submenu_cursor)
            inv_i = self.submenus.index(sub)
        
        if self.inventory.items:
            InventoryContextPanel.render(console,engine,self.inventory.items[self.submenu_cursor])
            
    def on_confirm(self):
        return self.submenus[self.submenu_cursor].on_confirm()

                
            

## menus contains submenus, submenus can be
#  an entity with their interactables(that can be clicked or navigated)
#  or a single column with only info
#  or an setting that can be changed clicking buttons

# might need to tell submenus form menu their root position so it nows where to move everything in it

class SubMenu:
    parent : BaseMenu
    def render(self,console: Console, engine: Engine, selected = False) -> None:
        raise NotImplementedError()
    
    def reposition(x,y,width,height):
        """handles positioning of the elements in the submenu, so they fit the given the dimensions provided"""
        raise NotImplementedError()
    
    def on_confirm(self):
        """activates the submenu option"""
        raise NotImplementedError()
    
    def navigate(dx):
        """tells the menus the player movement on the menu"""
        raise NotImplementedError()

class SingleOptionSubMenu(SubMenu):

    def __init__(self,parent : BaseMenu, content : str, onSelected :function) -> None:
        self.parent = parent
        self.button = Button(0,0,content)
        self.onSelected = onSelected

    def render(self,console: Console, engine: Engine) -> None:
        self.button.render(console,engine)
        
        

class MultiOptionSubMenu(SubMenu):
    cursor = 0
    def __init__(self,title , optionList : list, onSelectedList:list) -> None:
        self.title = title
        self.buttons = [ Button(0,0,title,on_click=on_click)for title,on_click in zip(optionList,onSelectedList) ]
        
    def render(self,console: Console, engine: Engine,selected) -> None:
        console.print(self.x,self.y+1,self.title)
        for i, b in enumerate(self.buttons):
            if selected and i == type(self).cursor:
                b.fg = color.button_hover
            else:
                b.fg = color.button_color
            b.render(console,engine)
        
            
    def reposition(self,x, y, width, height):
        self.x= x
        self.y = y
        self.width = width
        self.height=height
        for i,b in enumerate(self.buttons):
            b.x = x + width - 7 - 8*i
            b.y = y
            
    def navigate(self,dx):
        type(self).cursor += dx
        type(self).cursor %= len(self.buttons) 
        
    def set_cursor(self,x):
        type(self).cursor = x
        
    def on_confirm(self):
        return self.buttons[type(self).cursor].on_click()
        
        
            

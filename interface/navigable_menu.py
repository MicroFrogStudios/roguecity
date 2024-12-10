from __future__ import annotations
from typing import TYPE_CHECKING

import tcod
from tcod.console import Console



from config import screen_height, screen_width
from interface.render_functions import wrap
from components.inventory_component import Inventory
from engine import Engine
import config
from enums import color
from interface.button import Button
from tcod import libtcodpy

if TYPE_CHECKING:
    from tcod.console import Console
    from engine import Engine
    from classes.entity import Entity
    from components.fighter_component import Fighter
    from classes.item import Equipable


class Container:
    def __init__(self, x = 0, y = 0,
                 width = config.screen_width,
                 height = config.screen_height,
                 padding = 0,parent = None ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.padding = padding
        self.parent = parent

    def render(self,console: Console, engine:Engine):
        raise NotImplementedError()
    
    def on_confirm(self):
        raise NotImplementedError()
    
    def navigate(self,dx,dy):
        raise NotImplementedError()
    
    def set_cursor(self,x,y):
        raise NotImplementedError()

    def reposition(self,x=None,y=None,width=None,height=None):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height

    def menu_buttons(self)-> list[tuple[tuple[int,int],Button]]:
        raise NotImplementedError()

class TabContainer(Container):
    def __init__(self,tabs :list[BaseMenu], x = 0, y = 0, width = config.screen_width ,height = config.screen_height,tab_cursor = 0) -> None:
        super().__init__(x,y,width,height)
        self.tabs: list[BaseMenu] = tabs
        self.tabButtons: list[Button] = []
        for i, tab in enumerate(self.tabs):
            tab.parent = self
            tab_width = len(tab.name)+2
            self.tabButtons.append(Button(x=self.x,y = self.y,height=3,width=tab_width,title=tab.name,on_click=lambda n=i: self.set_cursor(z=n),framed=False)
)
        self.tab_cursor = tab_cursor
        
        
    def render(self,console: Console, engine: Engine):
        console.draw_frame(self.x,self.y,self.width,self.height,bg=color.black,fg=color.interface_lowlight,clear=True)
        width_acc = 0
        for i, tab in enumerate(self.tabs):
            
            tab_width = len(tab.name)+2
            self.tabButtons[i].x = self.x+ width_acc
                
            if i == self.tab_cursor:
                self.tabButtons[i].underscore = True
                # self.tabButtons[i].decoration = "┌─┐│ ││ │"
                # self.tabButtons[i].fg=color.white
                # console.draw_frame(x=self.x+ width_acc,y = self.y,height=3,width=tab_width,decoration="┌─┐│ ││ │")
                # console.print(x=self.x+ width_acc+tab_width//2,y = self.y+1,string=tab.name,fg=color.button_text,alignment=libtcodpy.CENTER)
                tab.render(console,engine)
            else:
                self.tabButtons[i].underscore = False
                # console.draw_frame(x=self.x+ width_acc,y = self.y,height=3,width=tab_width)
                # console.print(x=self.x+ width_acc+tab_width//2,y = self.y+1,string=tab.name,alignment=libtcodpy.CENTER)
                # self.tabButtons[i].decoration = "┌─┐│ │└─┘"
                # self.tabButtons[i].fg=color.button_color
                
            self.tabButtons[i].render(console,engine)
              
            width_acc += tab_width
              
    def navigate(self,dx,dy,dz=0):
        self.current_tab.navigate(dx,dy)
        self.tab_cursor += dz
        self.tab_cursor %= len(self.tabs)
    def on_confirm(self):
        return self.current_tab.on_confirm()
    
    def set_cursor(self,x=None,y=None,z=None):
        if x is not None and y is not None:
            self.current_tab.set_cursor(x,y)
        if z is not None:
            self.tab_cursor = z
        
    @property          
    def current_tab(self) -> BaseMenu:
        return self.tabs[self.tab_cursor]


class BaseMenu(Container):
    
    def __init__(self,name, submenus, padding = 0,parent = None, x=0,y=0,width=0,height=0) -> None:
        super().__init__(x,y,width,height,padding=padding,parent=parent)
        self.submenus : list[SubMenu] = submenus
        self.submenu_cursor : int = 0
        self.name = name
        
    def navigate(self,dx,dy):
        raise NotImplementedError()
    
    def menu_buttons(self)-> list[tuple[tuple[int,int],Button]]:
        raise NotImplementedError()
    

class HistoryViewer(BaseMenu):
    
    def __init__(self, name,engine : Engine, padding=3, parent=None, x=0, y=0, width=0, height=0):
        super().__init__(name, None, padding, parent, x, y, width, height)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1
    
    def navigate(self, dx, dy):
        self.cursor += dy
        self.cursor %= self.log_length
    
    def menu_buttons(self):
        return []
    def render(self, console, engine):
        
        log_console = tcod.console.Console(self.width - 2**self.padding, self.height - 4)

        # Draw a frame with a custom banner title.
        # log_console.draw_frame(self.x, self.y, log_console.width, log_console.height)
        # log_console.print_box(
        #     0, 0, log_console.width, 1, "┤Message history├", alignment=tcod.libtcodpy.CENTER
        # )

        # Render the message log using the cursor parameter.
        engine.message_log.render_messages(
            log_console,
            self.x+self.padding,
            self.y+2,
            log_console.width - 2,
            log_console.height - 2,
            engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)
    
class ContextPanelMenu(BaseMenu):

    def __init__(self,x,y,width, entity: Entity, engine :Engine = None, padding=1,navigable=False,parent=None) -> None:
        submenus :list[SubMenu] = [
            Textbox(entity.name,self),
            Imagebox(entity.icon, self),
            Textbox(entity.description, self),
            ]
        
        if hasattr(entity,"fighter"):
            fighter : Fighter = entity.fighter
            submenus.append(ProgressBar(self,fighter.max_hp,fighter.hp,"HP"))
            submenus.append(FighterStatBlock(self,fighter))
            
        if hasattr(entity,"equipped"):
            entity : Equipable
            submenus.append(EquipStatBlock(self,entity))
        
        self.navigable = navigable
        if navigable:
            buttons = [Button(0,0,
                              inter.name,disabled=not inter.check_player_activable(),
                              on_click=lambda i = inter : i.get_action(engine.player.interactor)) for inter in entity.get_interactables()]
            if buttons:
                self.buttons = ButtonMatrix(self,buttons)
                submenus.append(self.buttons)
                self.has_focus = False
            else:
                self.navigable = False
         
        
        height = 1
        previous_menus_height = 0
        for sub in submenus:
            sub.reposition(x=x+padding,y=y+previous_menus_height+padding,width=width-padding*2)
            height+= sub.height + padding
            previous_menus_height += sub.height + padding
        super().__init__(entity.name, submenus, padding,x=x,y=y,width=width,height=height,parent=parent)
    
    def render(self, console: Console, engine: Engine):
        if self.parent is None:
            console.draw_frame(x=self.x, y=self.y, width=self.width, height=self.height,clear=True,fg=color.menu_border,bg=color.black )
        for sub in self.submenus:
            sub.render(console,engine)
   
    def on_confirm(self):
        if self.navigable:
            return self.buttons.on_confirm()
    def navigate(self, dx, dy):
        if self.navigable:
            return self.buttons.navigate(dx, dy)
        
    def menu_buttons(self) -> list[tuple[tuple[int, int], Button]]:
        if self.navigable:
            return [((y,x),button) for x,row in enumerate(self.buttons.buttons) for y,button in enumerate(row)]
    
    def set_cursor(self, x, y):
        if self.navigable:
            return self.buttons.set_cursor(x, y)
        
    def reposition(self, x=None, y=None, width=None, height=None):
        super().reposition(x, y, width)
        height = 1
        previous_menus_height = 0
        for sub in self.submenus:
            sub.reposition(x=self.x+self.padding,y=self.y+previous_menus_height+self.padding,width=self.width-self.padding*2)
            height+= sub.height + self.padding
            previous_menus_height += sub.height + self.padding
        
        super().reposition(height=height)
                
class MapContextContainer(Container):
    def __init__(self, entities :list[Entity], engine, x=0, y=0, width=config.screen_width, height=config.screen_height) -> None:
        super().__init__(x,y,width,height)
        self.entities :list[Entity] = entities
        self.tab_cursor = 0
        self.engine = engine
        self.current_tab : ContextPanelMenu = ContextPanelMenu(self.x,self.y+3,self.width,self.entities[self.tab_cursor],engine,navigable=True,parent=self)
        self.height = self.current_tab.height+3
        self.border_color = color.menu_border
        self.tabButtons: list[Button] = []
        for i, entity in enumerate(self.entities):
            self.tabButtons.append(Button(x=self.x,y = self.y+1,height=2,width=1,title="?",on_click=lambda n=i: self.set_cursor(z=n),framed=False)
)
    
    def navigate(self, dx, dy,dz=0):
        if dz != 0:
            self.tab_cursor += dz
            self.tab_cursor %= len(self.entities)
            self.current_tab = ContextPanelMenu(self.x,self.y+3,self.width,self.entities[self.tab_cursor],self.engine,navigable=True,parent=self)
            self.height = self.current_tab.height+3
        self.current_tab.navigate(dx,dy)
        
    @property
    def current_entity(self):
        return self.entities[self.tab_cursor]
    
    def render(self, console: Console, engine: Engine):
        console.draw_frame(self.x,self.y,self.width,self.height,bg=color.black,fg=self.border_color,clear=True)
        width_acc = 0
        for i, entity in enumerate(self.entities):
            
            tab_width = len(entity.char)+2
            tab_x = self.x+ width_acc+tab_width//2
            self.tabButtons[i].x = self.x+ width_acc
            if i == self.tab_cursor:
                # console.draw_frame(x=self.x+ width_acc,y = self.y,height=3,width=tab_width,decoration="       ─ ")
                console.print(x=tab_x,y = self.y+1,string=entity.char,fg=entity.fgColor,alignment=libtcodpy.CENTER)
                console.print(x=tab_x,y = self.y+1+1,string='─',fg=self.border_color,alignment=libtcodpy.CENTER)
                
                self.current_tab.render(console,engine)
            else:
                # console.draw_frame(x=self.x+ width_acc,y = self.y,height=3,width=tab_width)
                console.print(x=self.x+ width_acc+tab_width//2,y = self.y+1,string=entity.char,fg=entity.fgColor,alignment=libtcodpy.CENTER)
            
            # if i == self.tab_cursor:
            #     console.draw_frame(x=self.x+ width_acc,y = self.y,height=3,width=tab_width,decoration="┌─┐│ ││ │")
            #     console.print(x=self.x+ width_acc+tab_width//2,y = self.y+1,string=entity.char,fg=entity.fgColor,alignment=libtcodpy.CENTER)
            #     self.current_tab.render(console,engine)
            # else:
            #     console.draw_frame(x=self.x+ width_acc,y = self.y,height=3,width=tab_width)
            #     console.print(x=self.x+ width_acc+tab_width//2,y = self.y+1,string=entity.char,fg=entity.fgColor,alignment=libtcodpy.CENTER)
            
              
            width_acc += tab_width
    
    def on_confirm(self):
        return self.current_tab.on_confirm()
    
    def set_cursor(self,x=None,y=None,z=None):
        if x is not None and y is not None:
            self.current_tab.set_cursor(x,y)
        if z is not None:
            self.tab_cursor = z
            self.current_tab = ContextPanelMenu(self.x,self.y+3,self.width,self.entities[self.tab_cursor],self.engine,navigable=True,parent=self)
            self.height = self.current_tab.height+3
        
    def menu_buttons(self) -> list[tuple[tuple[int, int], Button]]:
        return self.current_tab.menu_buttons()
    
    def reposition(self, x=None, y=None, width=None, height=None):
        super().reposition(x, y, width, height)
        self.current_tab.reposition(x,y,width,height)
        
class ScrollingMenu(BaseMenu):
    def __init__(self, submenus, name,padding = 0, submenu_height=1,x=0,y=0,width=0,height=0) -> None:
        super().__init__(name,submenus,padding,x=x,y=y,width=width,height=height)        
        self.submenu_height = submenu_height
        
    def navigate(self,dx,dy):
        
        if len(self.submenus) > 0:
            self.submenu_cursor += dy
            self.submenu_cursor %= len(self.submenus) 
    
    def set_cursor(self,x,y):
        self.submenu_cursor = y
            
    @property
    def submenus_visible(self):
        return self.submenus[self.current_page*self.page_size:(self.current_page + 1)*self.page_size]
    
    @property
    def page_size(self):
        if self.parent:
            return (self.parent.height-4)//self.submenu_height
        else:
            return (self.height)//self.submenu_height
        
        
    @property
    def current_page(self):
        return self.submenu_cursor//self.page_size
        
    
    def render(self,console: Console, engine: Engine) -> None:
        for sub in self.submenus_visible:
            sub.render(console,engine)
            

@DeprecationWarning
class StatusMenu(BaseMenu):
    """hp, power,defense, magic, equipped stuff"""
    def __init__(self, entity :Entity, name) -> None:
        submenus = entity.description
        super().__init__(submenus, name)


class InventoryMenu(ScrollingMenu):
    """ Menu displaying an inventory"""
    
    def __init__(self, inventory : Inventory) -> None:
        self.inventory = inventory
        submenus = [MultiOptionSubMenu( item.name,self,
                                       [i.name for i in item.get_interactables()],
                                       [lambda i = inter: i.get_action(inventory.parent.interactor) for inter in item.get_interactables()])
                    for item in self.inventory.items]
        super().__init__(submenus, "INVENTORY",padding=3,submenu_height=4)
        
        
    def navigate(self, dx, dy):
        super().navigate(dx, dy)
        if len(self.submenus) > 0:
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
            panel = ContextPanelMenu(90,0,30,self.inventory.items[self.submenu_cursor],engine)
            panel.render(console,engine)
            # InventoryContextPanel.render(console,engine,self.inventory.items[self.submenu_cursor])
            
    def on_confirm(self):
        return self.submenus[self.submenu_cursor].on_confirm()

                
class OptionsMenu(ScrollingMenu):
    
    def __init__(self, name, optionTuples : list[tuple[str,function]], padding=0, submenu_height=3,x=0,y=0,height=0,width=0):
        submenus : list[SingleOptionSubMenu] = []
        for cont,fun in optionTuples:
            submenus.append(SingleOptionSubMenu(self,cont,fun))
            
        super().__init__(submenus, name, padding, submenu_height,x=x,y=y,width=width,height=height)
 
    def menu_buttons(self) ->list[tuple[tuple[int,int],Button]]:
        return [((0,i),s.button) for i, s in enumerate(self.submenus)]
    
    def render(self, console, engine):
        if self.parent:
                width = self.parent.width - self.padding*2
                self.x = self.parent.x + width//2
        else:
            console.draw_frame(x=self.x - self.width//2,y=self.y,height=self.height,width=self.width,bg=color.black,)
        for i, sub in enumerate(self.submenus_visible):
            if self.parent:
                y = self.parent.y + 4 + self.submenu_height*i
            else:
                y = self.y + 1 + self.submenu_height*i
            
                
            sub.reposition(self.x,y)
            sub.render(console,engine, self.submenu_cursor == i)
            
    def on_confirm(self):
        return self.submenus[self.submenu_cursor].on_confirm()

## menus contains submenus, submenus can be
#  an entity with their interactables(that can be clicked or navigated)
#  or a single column with only info
#  or an setting that can be changed clicking buttons

# might need to tell submenus form menu their root position so it nows where to move everything in it

class SubMenu:
    parent : BaseMenu
    
    def __init__(self,parent) -> None:
        self.parent=parent
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        
        
    def render(self,console: Console, engine: Engine, selected = False) -> None:
        raise NotImplementedError()
    
    def reposition(self,x=None,y=None,width=None,height=None):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
    
    def on_confirm(self):
        """activates the submenu option"""
        raise NotImplementedError()
    
    def navigate(dx):
        """tells the menus the player movement on the menu"""
        raise NotImplementedError()
    
    def set_cursor(self,x):
        raise NotImplementedError()

class ButtonMatrix(SubMenu):
    
    def __init__(self, parent,buttons:list[Button],columns = 3) -> None:
        super().__init__(parent)
        self.buttons :list[list[Button]] = []
        for c in range(len(buttons)//columns+1):
            self.buttons.append(buttons[c*columns:c*columns+columns])
        
        self.reposition(self.x,self.y,self.width)
        
        self.height = len(self.buttons)*4
        self.columns = columns        
        self.cursor_x = 0
        self.cursor_y = 0
       
        
    def reposition(self, x=None, y=None, width=None, height=None):
        super().reposition(x, y, width, height)
        for i,row in enumerate(self.buttons):
            for j,button in enumerate(row):
                button.x = self.x+2 + j*8
                button.y = self.y + i*4
    
    def navigate(self,dx,dy):
        
        self.cursor_y += dy
        self.cursor_y %= len(self.buttons)
        self.cursor_x += dx
        self.cursor_x %= len(self.buttons[self.cursor_y])
    
    def set_cursor(self, x,y):
        self.cursor_x = x
        self.cursor_y = y
            
    def on_confirm(self):
        focus_button = self.buttons[self.cursor_y][self.cursor_x]
        if focus_button.disabled:
            return
        return focus_button.on_click()
        
    def render(self, console: Console, engine: Engine) -> None:
        for i,row in enumerate(self.buttons):
            for j,b in enumerate(row):
                if  j == self.cursor_x and i == self.cursor_y and self.parent.has_focus:
                    b.fg = color.button_hover
                else:
                    b.fg = b.text_color
                b.render(console,engine)
        
class EquipStatBlock(SubMenu):
    def __init__(self, parent,item: Equipable,padding=1) -> None:
        super().__init__(parent)
        self.item = item
        self.height = 3
        self.padding = padding
       
    def render(self, console: Console, engine: Engine, selected=False) -> None:
        console.print(self.x+self.padding,self.y,"POWER",color.button_text)
        console.print(self.x+self.padding+8,self.y,f"{self.item.power_bonus}",color.white)
        
        console.print(self.x+self.padding+14,self.y,"MAGIC",color.button_text)
        console.print(self.x+self.padding+22,self.y,f"{self.item.magic_bonus}",color.white)

        console.print(self.x+self.padding+12,self.y,"│",color.white)
        console.print(self.x+self.padding+12,self.y+1,"│",color.white)
        console.print(self.x+self.padding+12,self.y+2,"│",color.white)
        
        
        console.print(self.x+self.padding,self.y+2,"HP",color.button_text)
        console.print(self.x+self.padding+8,self.y+2,f"{self.item.hp_bonus}",color.white)
        
        console.print(self.x+self.padding+14,self.y+2,"DEFENSE",color.button_text)
        console.print(self.x+self.padding+22,self.y+2,f"{self.item.defense_bonus}",color.white)
        

class FighterStatBlock(SubMenu):
    
    def __init__(self, parent, fighter :Fighter,padding=1) -> None:
        super().__init__(parent)
        self.fighter = fighter
        self.height = 5
        self.padding = padding
        
    def render(self, console: Console, engine: Engine, selected=False) -> None:
        console.print(self.x+self.padding,self.y,"POWER",color.button_text)
        console.print(self.x+self.padding+6,self.y,f"{self.fighter.power} + ({self.fighter.power_bonus})",color.white)
        
        console.print(self.x+self.padding,self.y+2,"MAGIC",color.button_text)
        console.print(self.x+self.padding+6,self.y+2,f"{self.fighter.magic} + ({self.fighter.magic_bonus})",color.white)

        console.print(self.x+self.padding,self.y+4,"DEFENSE",color.button_text)
        console.print(self.x+self.padding+8,self.y+4,f"{self.fighter.defense} + ({self.fighter.defense_bonus})",color.white)
        


class ProgressBar(SubMenu):
    def __init__(self, parent,max_value,current_value,label = "",
                 text_color = color.bar_text,
                 bar_color = color.bar_filled,
                 empty_color = color.bar_empty,padding=1) -> None:
        super().__init__(parent)
        self.height = 1
        self.max_value = max_value
        self.current_value = current_value
        self.label = label
        self.text_color = text_color
        self.bar_color = bar_color
        self.empty_color = empty_color
        self.padding=padding
        
    def render(self, console: Console, engine: Engine, selected=False) -> None:

        bar_width = int(float(self.current_value) / self.max_value * self.width-self.padding*2)

        console.draw_rect(x=self.x+self.padding, y=self.y, width=self.width-self.padding*2, height=1, ch=1, bg=self.empty_color)

        if bar_width > 0:
            console.draw_rect(
                x=self.x+self.padding, y=self.y, width=bar_width, height=1, ch=1, bg=self.bar_color
            )

        console.print(
            x=self.x + self.padding+1, y=self.y, string=f"{self.label}: {self.current_value}/{self.max_value}", fg=self.text_color
        )

class Imagebox(SubMenu):
    
    def __init__(self,path,parent) -> None:
        """images should be 56x30 for context panels"""
        super().__init__(parent)
        self.image = tcod.image.load(path)[:, :, :3]
        self.height = 15
        ## SEMI graphics must use 56*30 pixels resolution
        
    def render(self, console: Console, engine: Engine, selected=False) -> None:
        console.draw_semigraphics(self.image,self.x,self.y)
        

class Textline(SubMenu):
    def __init__(self,text,parent,align = libtcodpy.LEFT,fg =color.interface_highlight,bg = None, padding = 1) -> None:
        super().__init__(parent)
        self.text = text
        self.align = align
        self.fg = fg
        self.bg = bg
        self.height = 1
        self.padding = padding
        
    def render(self, console: Console, engine: Engine, selected=False) -> None:
        console.print(self.x + self.padding,self.y,self.text,fg=self.fg,bg=self.bg,alignment=self.align)

class Textbox(SubMenu):
    

    def __init__(self,text,parent,align = libtcodpy.LEFT,fg =color.white,bg = None,padding =1) -> None:
        super().__init__(parent)
        self.text = text
        self.align = align
        self.fg = fg
        self.bg = bg
        self.padding = padding
    
    @property
    def wrapped_text(self) -> list[str]:
        return list(wrap(self.text, self.width-2*self.padding))
    
    @property    
    def height(self):
        return len(self.wrapped_text)
    
    @height.setter
    def height(self,h:int):
        pass
    
    def render(self, console: Console, engine: Engine, selected=False) -> None:
        y_offset = 0
        for line in self.wrapped_text:
            console.print(x=self.x+self.padding, y=self.y + y_offset, string=line, fg=self.fg,bg=self.bg,alignment=self.align)
            y_offset += 1

class SingleOptionSubMenu(SubMenu):

    def __init__(self,parent : BaseMenu, content : str, onSelected :function) -> None:
        super().__init__(parent)
        self.button = Button(self.x,self.y,content,on_click=onSelected,decoration="         ",width=len(content))
        self.onSelected = onSelected

    def render(self, console, engine, selected=False):
        self.button.x = self.x -self.button.width//2
        self.button.y = self.y
        if selected:
            self.button.fg = color.white
        else:
            self.button.fg = self.button.text_color
        self.button.render(console,engine)
        
        
    def on_confirm(self):
        return self.onSelected()

class MultiOptionSubMenu(SubMenu):
    cursor = 0
    def __init__(self,title ,parent, optionList : list, onSelectedList:list) -> None:
        super().__init__(parent)
        self.title = title
        self.buttons = [ Button(0,0,title,on_click=on_click)for title,on_click in zip(optionList,onSelectedList) ]
        
    def render(self,console: Console, engine: Engine,selected) -> None:
        console.print(self.x,self.y+1,self.title,color.interface_highlight)
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
        type(self).cursor -= dx
        type(self).cursor %= len(self.buttons) 
        
    def set_cursor(self,x):
        type(self).cursor = x
        
    def on_confirm(self):
        return self.buttons[type(self).cursor].on_click()
        
        
            

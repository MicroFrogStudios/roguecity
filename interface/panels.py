from __future__ import annotations
from typing import TYPE_CHECKING
import tcod

from tcod.console import Console



import config
from enums import color



from interface.navigable_menu import MapContextContainer
from interface.render_functions import render_bar, wrap
from engine import Engine
if TYPE_CHECKING:
    from classes.entity import Entity
    from classes.item import Item





class ContextPanel:
    """
    Represent a side panel that shows information 
    about the world and interactions of the player
    """

    x_offset = 90
    left_margin = 3
    fg = color.white
    panel_width = 30
    desc_start_y = 20
    
    buttons = []
    
    @classmethod
    def render(cls, console: Console, engine: Engine, context_entity:Entity) -> None:
       
                
        # getting wrapped description list to infer height of panel
        desc_wrap_list = list(wrap(context_entity.description, 20))
        from interface.button import Button
        
        frame_height = min(50,cls.desc_start_y+len(desc_wrap_list)+10)
        console.draw_frame(x=cls.x_offset, y=0, width=cls.panel_width, height=frame_height,title=context_entity.name,clear=True,fg=cls.fg,bg=color.black )
        image = tcod.image.load(context_entity.icon)[:, :, :3]
        ## SEMI graphics must use 56*30 pixels resolution
        console.draw_semigraphics(image,cls.x_offset+ 1,1)
        if hasattr(context_entity,"fighter"):
            render_bar(console,context_entity.fighter.hp,context_entity.fighter.max_hp,26,cls.x_offset+2,17)
        
        y_offset = 0
        for line in desc_wrap_list:
            console.print(x=cls.x_offset+3, y=cls.desc_start_y + y_offset, string=line, fg=color.menu_text)
            y_offset += 1
        
        
        ordered_possible_button_positions = [(cls.x_offset+3+i*8,cls.desc_start_y+y_offset+1) for i in range(0,3)] + [(cls.x_offset+3+i*8,cls.desc_start_y+y_offset+5) for i in range(0,3)]
            
        
        cls.buttons = [Button(*ordered_possible_button_positions[index],
                              inter.name,
                              on_click= lambda i = inter: i.get_action(engine.player.interactor))
                    if inter.check_player_activable()
                    else Button(*ordered_possible_button_positions[index],inter.name,fg=color.button_grey,text_color=color.button_grey,hover=color.button_grey) 
                    for index, inter in enumerate(context_entity.get_interactables())]
        for b in cls.buttons:
            if b.on_click and b.hovering(engine):
                b.fg = color.button_hover
            else:
                b.fg = color.button_color
            b.render(console,engine)
    
class MapContextPanel(ContextPanel):
    entities = None
    container = None
    
    @classmethod
    def set_entities(cls,entities,engine):
        cls.entities= entities
        cls.container = MapContextContainer(entities,engine,0,0,cls.panel_width)
            
    @classmethod
    def render(cls, console: Console, engine: Engine,selected=False) -> None:
        
        # checks if selected map entitity
        if selected:
            cls.container.border_color = color.interface_highlight
        else:
            entities = engine.check_visible_entities_on_mouse()
            if entities:
                cls.container = MapContextContainer(entities,engine,0,0,cls.panel_width)
            else:
                return
            
            # avoiding entity on map to render panel on opossing side
        cls.container.reposition(x= 90)
        if cls.container.current_entity.x >= config.screen_width//2:
            cls.container.reposition(x= 0)
            
        cls.container.render(console,engine)
                
            
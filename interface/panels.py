from typing import TYPE_CHECKING
import tcod

from tcod.console import Console

from classes.actor import Actor
from classes.entity import Entity
import config
from enums import color



from interface.render_functions import render_bar, wrap
from map.game_map import GameMap
from engine import Engine

class ContextPanel:
    """
    Represent a side panel that shows information 
    about the world and interactions of the player
    """

    x_offset = 90
    left_margin = 3
    fg = color.white
    
    @classmethod
    def render(cls, console: Console, engine: Engine) -> None:
        if engine.entities:
            entities = engine.entities
            cls.fg = color.invalid
        else:
            entities = engine.check_visible_entities_on_mouse()
            cls.fg = color.white
        #for now just use the first
        if entities:

            top_entity : Entity = entities[0]
            cls.x_offset = 90
            if top_entity.x >= config.screen_width//2:
                cls.x_offset = 0
            desc_wrap_list = list(wrap(top_entity.description, 20))
            from interface.button import Button
  
            # interaction_buttons = [ Button() for i in top_entity.interactables]  
            
            
            
            frame_height = min(50,20+8+len(desc_wrap_list)+2)
            console.draw_frame(x=cls.x_offset, y=0, width=30, height=frame_height,title=top_entity.name,clear=True,fg=cls.fg,bg=color.black )
            image = tcod.image.load(top_entity.icon)[:, :, :3]
            ## SEMI graphics must use 56*30 pixels resolution
            console.draw_semigraphics(image,cls.x_offset+ 1,1)
            if isinstance(top_entity, Actor):
                render_bar(console,top_entity.fighter.hp,top_entity.fighter.max_hp,26,cls.x_offset+2,17)
            y = 20
            y_offset = 0
            for line in desc_wrap_list:
                console.print(x=cls.x_offset+3, y=y + y_offset, string=line, fg=color.menu_text)
                y_offset += 1
                
            col_count = 0
            row_count = 0
            row_one_button_slots = [(cls.x_offset+3+i*8,y+y_offset+1) for i in range(0,3)]
            row_two_button_slots = [(cls.x_offset+3+i*8,y+y_offset+5) for i in range(0,3)]
            
            for xb,yb in row_one_button_slots:    
                Button(xb,yb,7,3,"tests").render(console,engine)
                
            for xb,yb in row_two_button_slots:    
                Button(xb,yb,7,3,"tests").render(console,engine)
                

        
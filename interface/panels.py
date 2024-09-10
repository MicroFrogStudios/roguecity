from typing import TYPE_CHECKING
import tcod

from tcod.console import Console


import config
from enums import color



from interface.render_functions import render_bar, wrap
from engine import Engine

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
    def render(cls, console: Console, engine: Engine) -> None:
        if engine.entities:
            entities = engine.entities
            cls.fg = color.menu_selected
        else:
            entities = engine.check_visible_entities_on_mouse()
            cls.fg = color.white
        #for now just use the first
        if entities:

            top_entity = entities[0]
            cls.x_offset = 90
            if top_entity.x >= config.screen_width//2:
                cls.x_offset = 0
            desc_wrap_list = list(wrap(top_entity.description, 20))
            from interface.button import Button
  
            # interaction_buttons = [ Button() for i in top_entity.interactables]  
            
            
            
            
            frame_height = min(50,cls.desc_start_y+len(desc_wrap_list)+10)
            console.draw_frame(x=cls.x_offset, y=0, width=cls.panel_width, height=frame_height,title=top_entity.name,clear=True,fg=cls.fg,bg=color.black )
            image = tcod.image.load(top_entity.icon)[:, :, :3]
            ## SEMI graphics must use 56*30 pixels resolution
            console.draw_semigraphics(image,cls.x_offset+ 1,1)
            if hasattr(top_entity,"fighter"):
                render_bar(console,top_entity.fighter.hp,top_entity.fighter.max_hp,26,cls.x_offset+2,17)
           
            y_offset = 0
            for line in desc_wrap_list:
                console.print(x=cls.x_offset+3, y=cls.desc_start_y + y_offset, string=line, fg=color.menu_text)
                y_offset += 1
            
            
            ordered_possible_button_positions = [(cls.x_offset+3+i*8,cls.desc_start_y+y_offset+1) for i in range(0,3)] + [(cls.x_offset+3+i*8,cls.desc_start_y+y_offset+5) for i in range(0,3)]
               
            
            cls.buttons = [Button(*ordered_possible_button_positions[index],inter.name,on_click=inter.get_action)
                       if inter.check_player_activable()
                       else Button(*ordered_possible_button_positions[index],inter.name,fg=color.button_grey,hover=color.button_grey) 
                       for index, inter in enumerate(top_entity.interactables)]
            
            for b in cls.buttons:
                b.render(console,engine)

                

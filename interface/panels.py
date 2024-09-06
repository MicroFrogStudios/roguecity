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

class RightPanel:
    """
    Represent a side panel that shows information 
    about the world and interactions of the player
    """
    entities: list[Entity] = None
    x_offset = 90
    left_margin = 3
    
    
    @classmethod
    def render(cls, console: Console, engine: Engine) -> None:
        cls.render_names_at_mouse_location(console,engine)
        
        
    @classmethod
    def render_names_at_mouse_location(cls,
        console: Console, engine: Engine
    ) -> None:
        
        #for now just use the first
        if cls.entities:
            
            top_entity : Entity = cls.entities[0]
            desc_wrap_list = list(wrap(top_entity.description, 20))
            frame_height = min(50,20+len(desc_wrap_list)+2)
            console.draw_frame(x=cls.x_offset, y=0, width=30, height=frame_height,title=top_entity.name,clear=True,fg=color.white,bg=color.black )
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

          
            
    
    @classmethod
    def check_entities_at_location(cls,engine: Engine) -> None:
        x,y = engine.mouse_location
        
        if not engine.game_map.in_bounds(x, y) or not engine.game_map.visible[x, y]:
            cls.entities =  []
            return
        cls.x_offset = 90
        if x >= config.screen_width//2:
            cls.x_offset = 0
        cls.entities =  [
            entity for entity in engine.game_map.entities if entity.x == x and entity.y == y
        ]
        
        
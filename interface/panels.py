from typing import TYPE_CHECKING
import tcod

from tcod.console import Console

from classes.actor import Actor
from classes.entity import Entity
from enums import color



from interface.render_functions import render_bar, wrap
from map.game_map import GameMap
from engine import Engine

class RightPanel:
    """
    Represent a side panel that shows information 
    about the world and interactions of the player
    """
    current_entity: Entity = None
    x_offset = 90
    left_margin = 3
    
    
    @classmethod
    def render(cls, console: Console, engine: Engine) -> None:
        cls.render_names_at_mouse_location(console,engine)
        
        
    @classmethod
    def render_names_at_mouse_location(cls,
        console: Console, engine: Engine
    ) -> None:
        mouse_x, mouse_y = engine.mouse_location
        entities = cls.get_entities_at_location(
            x=mouse_x, y=mouse_y, game_map=engine.game_map
        )
        #for now just use the first
        if entities:
            cls.current_entity = entities[0]
            console.draw_frame(x=cls.x_offset, y=0, width=30, height=50,title=cls.current_entity.name,clear=True,fg=color.white,bg=color.black )
            image = tcod.image.load(cls.current_entity.icon)[:, :, :3]
            ## SEMi graphics must use 56*30 pixels resolution
            console.draw_semigraphics(image,cls.x_offset+ 1,1)
            if isinstance(cls.current_entity, Actor):
                render_bar(console,cls.current_entity.fighter.hp,cls.current_entity.fighter.max_hp,26,92,17)
            y = 20
            y_offset = 0
            # console.print(x=90+2, y= 21, string=cls.current_entity.description)
            for line in list(wrap(cls.current_entity.description, 20)):
                console.print(x=cls.x_offset+3, y=y + y_offset, string=line, fg=color.menu_text)
                y_offset += 1
        else:
            console.draw_frame(x=cls.x_offset, y=0, width=30, height=50,clear=True,fg=color.white,bg=color.black )
            
            
    
    @staticmethod
    def get_entities_at_location(x: int, y: int, game_map: GameMap) -> str:
        if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
            return ""

        entities =  [
            entity for entity in game_map.entities if entity.x == x and entity.y == y
        ]

        return entities
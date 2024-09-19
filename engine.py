from __future__ import annotations

import lzma
import pickle
from typing import TYPE_CHECKING
from tcod.console import Console

from enums import color
from interface.message_log import MessageLog

from tcod.map import compute_fov
import exceptions
import tcod.constants as tconst
import config
import interface.render_functions as rend

if TYPE_CHECKING:
  
    from map.game_map import GameMap, GameWorld
    from classes.actor import Actor
    

class Engine:
    game_map: GameMap
    game_world: GameWorld
    

    def __init__(self, player: Actor):
        self.player = player
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        # Camera view, cant be bigger than console.
        self.camera_width = config.screen_width
        self.camera_height = config.screen_height -10
        self.camera_x_offset = 0
        (self.x_left_ref,self.x_right_ref, self.y_left_ref, self.y_right_ref) = (0,0,self.camera_width,self.camera_height)
        self.entities = None

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass # Ignore impossible action exceptions from AI.

    def render(self, console: Console) -> None:
        
        
        self.update_camera_references()
        self.game_map.render(console)
        self.message_log.render(console=console,x=21,y=45, width=40, height=5)
        rend.hline(console,0,config.screen_height-9)
        rend.render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,x=0,y=45
        )
        rend.render_dungeon_level(
            console=console,
            dungeon_level=self.game_world.current_floor,
            location=(0, 47),
        )
        
        
    def check_visible_entities_on_mouse(self):
        x,y = self.mouse_location
        
        if not self.game_map.in_bounds(x, y) or not self.game_map.visible[x, y]:
            return  []
            
        return  [
            entity for entity in self.game_map.entities if entity.x == x and entity.y == y and entity is not self.player
        ]  

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8, light_walls= True, 
            algorithm=tconst.FOV_SYMMETRIC_SHADOWCAST
        )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)

    def map_to_camera_coordinates(self,map_x,map_y):
        return (map_x - self.x_left_ref + self.camera_x_offset, map_y - self.y_left_ref)

    def camera_to_map_coordinates(self,camera_x,camera_y):
        return (camera_x + self.x_left_ref - self.camera_x_offset, camera_y + self.y_left_ref)

    def update_camera_references(self):

        x_left = self.player.x-self.camera_width//2
        x_right = self.player.x+self.camera_width//2

        if x_left < 0:
            x_right =self.camera_width
            x_left = 0
        if x_right > self.game_map.width:
            x_left = self.game_map.width - self.camera_width
            x_right = self.game_map.width

        y_left = self.player.y-self.camera_height//2
        y_right = self.player.y+self.camera_height//2
        
        if y_left < 0:
            y_right =self.camera_height
            y_left = 0
        if y_right > self.game_map.height:
            y_left = self.game_map.height - self.camera_height
            y_right = self.game_map.height

        (self.x_left_ref,self.x_right_ref, self.y_left_ref, self.y_right_ref) = (x_left,x_right,y_left,y_right)

    def in_camera_view(self,map_x,map_y):
          return (map_x > self.x_left_ref and
            map_x < self.x_right_ref and
            map_y > self.y_left_ref and
            map_y < self.y_right_ref)
        
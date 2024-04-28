from __future__ import annotations

from typing import TYPE_CHECKING

from tcod.context import Context
from tcod.console import Console

from inputHandlers import EventHandler
from tcod.map import compute_fov
import tcod.constants as tconst

if TYPE_CHECKING:
    from classes.entity import Entity
    from map.game_map import GameMap

class Engine:
    game_map: GameMap

    def __init__(self, player: Entity):
        self.event_handler: EventHandler = EventHandler(self)
        self.player = player

    def handle_enemy_turns(self) -> None:
        for entity in self.game_map.entities - {self.player}:
            print(f'The {entity.name} wonders when it will get to take a real turn.')

    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)
        context.present(console)
        console.clear()

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

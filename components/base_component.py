from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from classes.entity import Entity
    from map.game_map import GameMap


class BaseComponent:
    parent: Entity  # Owning entity instance.

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap
    @property
    def engine(self) -> Engine:
        return self.gamemap.engine # por añadir en entity pero necesario
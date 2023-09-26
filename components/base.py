from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine
    from classes.entity import Entity


class BaseComponent:
    entity: Entity  # Owning entity instance.

    @property
    def engine(self) -> Engine:
        return self.entity.gamemap.engine # por añadir en entity pero necesario
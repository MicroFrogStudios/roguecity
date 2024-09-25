from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from classes.actor import Actor

from components.base_component import BaseComponent


class Interactor(BaseComponent):
    parent : Actor
    """
    Component that flags an entity as one capable 
    of activating interactables
    """
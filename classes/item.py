from typing import Tuple
from classes.entity import Entity
from components.interactable_component import PickUpInteractable,DropInteractable, Interactable
from components.inventory_component import Inventory
from enums.render_order import RenderOrder


class Item(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        description: str = "<Missing Description>",
        icon : str = "assets\sprites\\red_egg.png",
        interactables : list[Interactable] = [],
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            fgColor=color,
            name=name,
            description=description,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
            icon = icon,
            interactables = interactables
            
        )
        
        self.pickUpInteractable = PickUpInteractable()
        self.pickUpInteractable.parent = self
        
        self.dropInteractable = DropInteractable()
        self.dropInteractable.parent = self
           
    def get_interactables(self) -> set[Interactable]:
        # TODO add default item interactables grab or drop
        if isinstance(self.parent,Inventory):
            return self.interactables + [self.dropInteractable]
        else:
            return self.interactables + [self.pickUpInteractable]
            
    
    
    def set_interactables(self, interactables:set[Interactable]):
        self.interactables = interactables
        
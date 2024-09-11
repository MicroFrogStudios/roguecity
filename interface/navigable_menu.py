from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tcod.console import Console
    from engine import Engine

class Tab:
    
    def __init__(self,name, menu) -> None:
        self.name=name
        self.menu=menu



class TabContainer:
    tabs: list[Tab]


class BaseMenu():
    
    def render(console: Console, engine: Engine) -> None:
        raise NotImplementedError()
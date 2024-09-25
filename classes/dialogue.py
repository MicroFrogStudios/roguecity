from __future__ import annotations

from typing import  TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from components.interactable_component import Interactable
    from engine import Engine


class Dialogue():
    
    def __init__(self,lines :list[str], triggers :list[Callable[[Engine,Interactable]]]) -> None:
        self.lines :list[str] = lines
        self.triggers = triggers

        self.talk_count = 0
        
    def get_next_line(self, engine: Engine, inter :Interactable):
        
        count =self.talk_count
        self.talk_count += 1
        self.talk_count = min(len(self.lines)-1, self.talk_count)

        if self.triggers[count] is not None:
            self.triggers[count](engine,inter)
            
        return self.lines[count]
    
    
        
        
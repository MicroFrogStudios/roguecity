



from typing import Optional
from components.ai import PlayerAI


class PlayerController:
      
    instance = None
    def __init__(self,player) -> None:
        self.player = player
        self.aiList :list[PlayerAI] = []
        self.current_task : Optional[PlayerAI] = None
        self.turns_confused = 0
        self.turns_invisible = 0
    
    def next(self) -> PlayerAI:
        return self.aiList.pop(0)
    
    def interrupt(self):
        self.current_task = None
        self.aiList = []
    
    def hasNext(self) -> bool:
        return len(self.aiList) > 0
    
    @classmethod
    def get_instance(cls,player=None):
        if cls.instance is None:
            cls.instance = PlayerController(player)
        return cls.instance
        
    
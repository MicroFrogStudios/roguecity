from enum import auto, Enum


class RenderOrder(Enum):
    CORPSE = auto()
    PROP = auto()
    ITEM = auto()
    ACTOR = auto()
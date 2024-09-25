from classes.dialogue import Dialogue
from components.interactable_component import TalkInteraction
from engine import Engine
from enums import color


def old_man_gift(engine:Engine, inter:TalkInteraction):
    
    inv = inter.parent.inventory
    if len(inv.items) > 0:
        gift = inv.items[0]
        inv.drop(gift)
        gift.x = engine.player.x
        gift.y = engine.player.y
        engine.message_log.add_message("The old man drops something at your feet")
    

old_man_dialogue = Dialogue([
    "I should warn you, if you wander this lost city you will become lost yourself.",
    "If you must wander then at least let me give you this.",
    "I hope you succeed in your endeavors. Be wary of the stairs."
],[None,
   old_man_gift
   ,None])
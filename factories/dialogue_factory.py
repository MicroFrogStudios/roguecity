from classes.dialogue import Dialogue
from components.interactable_component import TalkInteraction
from engine import Engine
from enums import color
from components import ai

def old_man_gift(engine:Engine, inter:TalkInteraction):
    
    inv = inter.parent.inventory
    if len(inv.items) > 0:
        gift = inv.items[0]
        inv.drop(gift)
        gift.x = engine.player.x
        gift.y = engine.player.y
        engine.message_log.add_message("The old man drops something at your feet")




old_man_dialogue = Dialogue([
    "I should warn you, if you wander needlessly this lost city you will become lost yourself.",
    "If you must wander then at least let me give you this.",
    "They say it will hatch when it is at the correct depth.",
    "I hope you succeed in your endeavors. Be wary of the stairs."
],[None,
   old_man_gift
   ,None,None])


lost_warrior_dialogue_final = Dialogue([
    "Thank you for everything.",

],[None
   ])  

def lost_warrior_quest_final(engine:Engine, inter:TalkInteraction):
    inv = inter.parent.inventory
    if len(inv.items) > 0 and engine.key_conditions():
        gift = inv.items[0]
        inv.drop(gift)
        gift.x = engine.player.x
        gift.y = engine.player.y
        engine.message_log.add_message("The lost warrior says: You have it! the sacred frog!",color.welcome_text)
        engine.message_log.add_message("The warrior drops something at your feet")
        engine.message_log.add_message("The lost warrior says: This is the key. You earnt it",color.welcome_text)

        inter.dialogue = lost_warrior_dialogue_final
    else:
        engine.message_log.add_message("The lost warrior says: I wont leave this place without the frog i came looking for.",color.welcome_text)




lost_warrior_dialogue_frog = Dialogue([
    "you have my thanks for guiding me here, stranger..",
    "I wish i could open the door for you, but i still need something.",
    ""
],[None,None,
   lost_warrior_quest_final
   ])

def lost_warrior_quest_middle(engine:Engine, inter:TalkInteraction):
    pass


lost_warrior_dialogue_middle = Dialogue([
    "No time to talk, this are dangerous halls.",

],[
   None
   ])


def lost_warrior_quest_start(engine:Engine, inter:TalkInteraction):
    inter.dialogue = lost_warrior_dialogue_middle
    engine.message_log.add_message("The lost warrior has joined you!")
    inter.parent.friendly_ai = ai.FollowNeutral(inter.parent,engine.player,follow_distance=2)
    inter.parent.ai = inter.parent.friendly_ai
    inter.parent.actor_type = engine.player.actor_type
    engine.player_follower = inter.parent
    engine.lost_warrior_quest_state = "started"

lost_warrior_dialogue_start = Dialogue([
    "I am lost",
    "I need you to guide me to the exit."
],[None,
   lost_warrior_quest_start
   ])







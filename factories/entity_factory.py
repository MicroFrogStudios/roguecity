
from actions import MeleeAction
from classes.actor import Actor
from classes.item import Item, Equipable
from components import ai
from components.fighter_component import Fighter
import components.interactable_component as interactables
from enums import color
from components.inventory_component import Inventory
from factories import dialogue_factory

# Actors

player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    description= "This is you",
    friendly_ai=ai.IdleNeutral(),
    fighter=Fighter(hp=25, defense=0, power=1,magic=1),
    inventory=Inventory(capacity=27),
    icon= "assets\sprites\magito_azul.png",
    hostile=False,
    actor_type=Actor.Type.PLAYER
)
old_man = Actor(
    char="☻",
    color=(0,0,120),
    name="ragged old man",
    description= "Long beard, covered eyes, with midnight blue robes, wandering the tunnels. Maybe he can help",
    hostile=False,
    actor_type=Actor.Type.NPC,
    friendly_ai=ai.IdleNeutral(),
    hostile_ai= ai.HostileEnemy(),
    interactables=[interactables.TalkInteraction(dialogue_factory.old_man_dialogue),interactables.AssaultInteraction()],
    icon= "assets/sprites/magito_azul.png",
    fighter=Fighter(hp=999, defense=0, power=1,magic=10),
    inventory=Inventory(capacity=1),
    )

lost_warrior =  Actor(
    char="w",
    color=(177, 176, 154),
    name="Lost Warrior",
    description= "Shadow of a former soldier, driven mad by never-ending wander",
    hostile=True,
    actor_type=Actor.Type.MONSTER,
    friendly_ai=ai.RandomGait(5),
    hostile_ai=ai.HostileEnemy(),
    fighter=Fighter(hp=5, defense=1, power=2,magic=0),
    inventory=Inventory(capacity=2),
    icon= "assets\sprites\lost_warrior.png",
)
weak_skuly = Actor(
    char="i",
    color=(177, 176, 154),
    name="Walking skull",
    description= "Eerie skull walking on two legs. Harmless if left alone",
    hostile=False,
    actor_type=Actor.Type.MONSTER,
    friendly_ai=ai.RandomGait(3),
    hostile_ai=ai.HostileEnemy(),
    fighter=Fighter(hp=2, defense=0, power=1,magic=0),
    inventory=Inventory(capacity=0),
    icon= "assets\sprites\skuly.png",
    blood_color= (120, 116, 116),
    interactables=[interactables.AssaultInteraction(cry="Shrieeek!")],
)
rat_small = Actor(
    char="r",
    color=(100, 100, 100),
    name="rat",
    hostile=False,
    actor_type=Actor.Type.CRITTER,
    description="A small mammal looking for food",
    friendly_ai=ai.CuriousCritter(),
    hostile_ai= ai.HostileEnemy(),
    fighter=Fighter(hp=1, defense=0, power=1,magic=0),
    inventory=Inventory(capacity=0),
    interactables=[interactables.TauntInteraction(response="= ò · ó ="),interactables.PetInteraction(response="= ^ · ^ =")],
    icon= "assets/sprites/raticuli.png",
)

# ITEMS

food = Item(
    char="%",
    color=(153, 0, 0),
    name="food",
    icon="assets/sprites/meat.png",
    interactables=[interactables.EatInteraction(4)],
    description= "Heals you a certain amount"
    

)

lightning_scroll = Item(
    char="~",
    color=(255, 255, 0),
    name="Lightning Scroll",
    interactables=[interactables.LightningDamageConsumable(damage=20, maximum_range=5)],
    icon="assets/sprites/scroll_basic.png",
)

confusion_scroll = Item(
    char="~",
    color=(207, 63, 255),
    name="Confusion Scroll",
    interactables=[interactables.ConfusionConsumable(number_of_turns=10)],
    icon="assets/sprites/scroll_basic.png",
)

fireball_scroll = Item(
    char="~",
    color=(255, 0, 0),
    name="Fireball Scroll",
    interactables=[interactables.FireballDamageConsumable(damage=12, radius=3)],
    icon="assets/sprites/scroll_basic.png",
)

mystery_egg = Item(
    char="o",
    color=(240,0,0),
    name= "Mysterious Egg",
    description="Red egg emanating a strange power",
    icon = "assets/sprites/red_egg.png"
    
)

from components.inventory_component import Equipment as eq

broken_sword = Equipable(
    char="/",
    color=color.gray,
    name="Broken sword",
    description="Dull sword missing its tip.",
    eq_type=eq.Type.WEAPON,
    power_bonus=1,
    icon="assets/sprites/broken_sword.png",
)

worn_outfit = Equipable(
    char="[",
    color=color.gray,
    name="worn outfit",
    description="It has some holes but it covers you mostly.",
    eq_type=eq.Type.ARMOR,
    defense_bonus=1,
    icon="assets/sprites/basic cloak.png"
    
)

amulet_health = Equipable(
    
    char="δ",
    color=color.white,
    name="Amulet of vitality",
    description="You can feel yourself healthier",
    eq_type=eq.Type.AMULET,
    hp_bonus=5,
    icon="assets/sprites/heart_amulet.png"
)

wooden_staff = Equipable(
    char="⌠",
    color=color.gray,
    name="Wooden staff",
    description="A simple wooden staff",
    eq_type=eq.Type.STAFF,
    magic_bonus=1,
    icon="assets/sprites/simple_staff.png"
)


from classes.prop import Prop

down_staircase = Prop(
    char="▼",
    color=color.wall_dark,
    name="Staircase",
    description="It goes down",
    icon="assets/sprites/downstairs.png",
    interactables=[interactables.DescendInteractable()]
)

up_staircase = Prop(
    char="▲",
    color=color.wall_dark,
    name="Staircase",
    description="It goes up",
    icon="assets/sprites/upstairs.png",
    interactables=[interactables.AscendInteractable()]
)
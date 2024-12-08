
from actions import MeleeAction
from classes.actor import Actor
from classes.item import Item, Equipable
from components import ai
from components.fighter_component import Fighter
import components.interactable_component as interactables
from enums import color
from components.inventory_component import Inventory
from factories import dialogue_factory

# ITEMS

food = Item(
    char="%",
    color=(153, 0, 0),
    name="food",
    icon="assets/sprites/meat.png",
    interactables=[interactables.EatInteraction(4)],
    description= "Heals you a certain amount",
    item_type= Item.Type.FOOD

)

little_shroom = Item(
    char="τ",
    color=color.moss_green,
    name="Cave shroom",
    icon="assets/sprites/shroom.png",
    interactables=[interactables.EatInteraction(2)],
    description= "Heals you a certain amount",
    item_type= Item.Type.FOOD

)

rock = Item(
    char="∙",
    color=color.stone_grey_dark,
    name="Round rock",
    icon="assets/sprites/rock.png",
    interactables=[interactables.throwInteraction(0)],
    description= "good for throwing",
    item_type= Item.Type.OTHER

)
teeth = Item(
    char="`",
    color=color.bone_light,
    name="Sharp tooth",
    icon="assets/sprites/teef.png",
    interactables=[interactables.throwInteraction(2)],
    description= "can be thrown like a dart",
    item_type= Item.Type.OTHER

)

lightning_scroll = Item(
    char="~",
    color=(255, 255, 0),
    name="Lightning Scroll",
    interactables=[interactables.LightningDamageConsumable(damage=5, maximum_range=5)],
    icon="assets/sprites/scroll_basic.png",
    item_type=Item.Type.SCROLL
)

confusion_scroll = Item(
    char="~",
    color=(207, 63, 255),
    name="Confusion Scroll",
    interactables=[interactables.ConfusionConsumable(number_of_turns=5)],
    icon="assets/sprites/scroll_basic.png",
    item_type=Item.Type.SCROLL
)

fireball_scroll = Item(
    char="~",
    color=(255, 0, 0),
    name="Fireball Scroll",
    interactables=[interactables.FireballDamageConsumable(damage=5, radius=5)],
    icon="assets/sprites/scroll_basic.png",
    item_type=Item.Type.SCROLL
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

nice_sword = Equipable(
    char="/",
    color=color.gray,
    name="Iron sword",
    description="Simpe sword in good condition.",
    eq_type=eq.Type.WEAPON,
    power_bonus=3,
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

nice_outfit = Equipable(
    char="[",
    color=color.gray,
    name="cloaked outfit",
    description="lost cloak that makes for a sturdy and comfy outfit.",
    eq_type=eq.Type.ARMOR,
    defense_bonus=3,
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

amulet__great_health = Equipable(
    
    char="δ",
    color=color.white,
    name="Amulet of vitality",
    description="You can feel yourself even healthier",
    eq_type=eq.Type.AMULET,
    hp_bonus=10,
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

nice_staff = Equipable(
    char="⌠",
    color=color.gray,
    name="Ominous staff",
    description="A glowing wooden staff",
    eq_type=eq.Type.STAFF,
    magic_bonus=3,
    icon="assets/sprites/simple_staff.png"
)

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
    char="☻",
    color=color.moss_green,
    name="lost warrior",
    description= "Shadow of a former soldier, only hope moves him forward",
    hostile=False,
    actor_type=Actor.Type.NPC,
    friendly_ai=ai.RandomGait(5),
    hostile_ai=ai.HostileEnemy(),
    fighter=Fighter(hp=10, defense=1, power=2,magic=0),
    inventory=Inventory(capacity=2),
    interactables=[interactables.AssaultInteraction()],
    icon= "assets\sprites\lost_warrior.png",
)
#monsters

wizzo = Actor(
    char="A",
    color=color.magic_purple,
    name="wizzo",
    description= "Strange apparition possessing arcane powers.",
    hostile=True,
    actor_type=Actor.Type.MONSTER,
    friendly_ai=ai.RandomGait(5),
    hostile_ai=ai.MageEnemy(range_dist=3,hitchance=30),
    fighter=Fighter(hp=4, defense=0, power=0,magic=1),
    inventory=Inventory(capacity=2),
    blood_color=color.magic_green,
    interactables=[interactables.ScareInteraction()],
    icon= "assets\sprites\wizzo.png",
    loot_table={"items":  [lightning_scroll, fireball_scroll,confusion_scroll],
                "weights":[0.5,             0.5,                0.5]}
)
archwizzo = Actor(
    char="Å",
    color=color.magic_purple,
    blood_color=color.magic_green,
    name="arch wizzo",
    description= "Strange apparition possessing arcane powers.",
    hostile=True,
    actor_type=Actor.Type.MONSTER,
    friendly_ai=ai.RandomGait(5),
    hostile_ai=ai.MageEnemy(),
    fighter=Fighter(hp=8, defense=0, power=0,magic=3),
    inventory=Inventory(capacity=2),
    interactables=[interactables.ScareInteraction()],
    icon= "assets\sprites\wizzo.png",
    loot_table={"items":  [lightning_scroll, fireball_scroll,confusion_scroll],
                "weights":[0.33,             0.33,                0.33]}
)

hungryhead =  Actor(
    char="Θ",
    color=color.monster_blue,
    name="hungry head",
    description= "Very hungry, eating is the only thing it can think off.",
    hostile=True,
    actor_type=Actor.Type.MONSTER,
    friendly_ai=ai.RandomGait(5),
    hostile_ai=ai.HungryEnemy(),
    fighter=Fighter(hp=10, defense=0, power=2,magic=0),
    inventory=Inventory(capacity=2),
    interactables=[interactables.GiveFood()],
    icon= "assets\sprites\hungryhead.png",
    loot_table={"items":  [food, teeth],
                "weights":[0.1,  1]}
)

hungryhead_shiny =  Actor(
    char="Θ",
    color=color.monster_shine,
    name="shiny hungry head",
    description= "Very hungry, eating is the only thing it can think off.",
    hostile=True,
    actor_type=Actor.Type.MONSTER,
    friendly_ai=ai.RandomGait(5),
    hostile_ai=ai.HostileEnemy(),
    fighter=Fighter(hp=25, defense=2, power=5,magic=2),
    inventory=Inventory(capacity=2),
    interactables=[interactables.GiveFood()],
    icon= "assets\sprites\hungryhead.png",
    loot_table={"items":  [food, teeth],
                "weights":[0.1,  1]}
)

weak_skuly = Actor(
    char="o",
    color=color.bone_light,
    name="small walking skull",
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

strong_skuly = Actor(
    char="O",
    color=color.bone_light,
    name="giant walking skull",
    description= "Eerie skull walking on two legs. Harmless if left alone",
    hostile=False,
    actor_type=Actor.Type.MONSTER,
    friendly_ai=ai.RandomGait(5),
    hostile_ai=ai.HostileEnemy(),
    fighter=Fighter(hp=10, defense=1, power=3,magic=0),
    inventory=Inventory(capacity=0),
    icon= "assets\sprites\skuly.png",
    blood_color= (120, 116, 116),
    interactables=[interactables.AssaultInteraction(cry="Shrieeek!")],
    loot_table={"items":  [fireball_scroll, confusion_scroll, lightning_scroll, teeth],
                "weights":[0.3,              0.4,               0.4,             0.01]}
)
shroomed = Actor(
    char="♠",
    color=color.bone_light,
    name="shroomed",
    hostile=False,
    actor_type=Actor.Type.CRITTER,
    description="Walking mushroom, very shy, might be tasty...",
    friendly_ai=ai.RandomGait(2),
    hostile_ai= ai.FleeingEnemy(),
    fighter=Fighter(hp=5, defense=0, power=0,magic=1),
    inventory=Inventory(capacity=0),
    interactables=[interactables.BiteInteraction()],
    icon= "assets/sprites/shroomed.png",
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
    loot_table={"items":  [food, teeth],
                "weights":[0.6,  0.1]}
)
actorList =        [rat_small,shroomed,weak_skuly,strong_skuly,hungryhead,hungryhead_shiny,wizzo,archwizzo]
A_WeightUp_1_2 =   [0.5,       0,      1,          0.01,       0.1,        0.001,      0,          0,      ]
A_WeightDown_1_2 = [0,         0.5,    1,          0.02,       0,          0,         0.2,        0.01,   ]

A_WeightUp_3_4 =   [0.5,       0,      1,          0.5,       0.4,        0.2,       0,           0,      ]
A_WeightDown_3_4 = [0,         0.5,    1,          0.5,       0,          0,         0.4,         0.2,   ]





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
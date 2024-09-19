
from classes.actor import Actor
from classes.item import Item
from components.ai import HostileEnemy
from components.fighter_component import Fighter, Level
import components.interactable_component as interactables
from components.interactor_component import Interactor
from components.inventory_component import Inventory

player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    description= "This is you",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30, defense=2, power=5),
    interactor=Interactor(),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200),
    icon= "assets\sprites\magito_azul.png"
)

weak_skuly = Actor(
    char="i",
    color=(255, 255, 255),
    name="Lost skull",
    description= "Eerie skull walking on two legs. Harmless if left alone",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, defense=0, power=1),
    inventory=Inventory(capacity=0),
    interactor=Interactor(),
    level=Level(xp_given=35),
    icon= "assets\sprites\skuly.png",
    interactables=[interactables.TauntInteraction()],
)
troll = Actor(
    char="T",
    color=(0, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, defense=1, power=4),
    inventory=Inventory(capacity=0),
    interactor=Interactor(),
    level=Level(xp_given=100),
    interactables=[interactables.TauntInteraction()],
)

food = Item(
    char="%",
    color=(153, 0, 0),
    name="food",
    icon="assets/sprites/meat.png",
    interactables=[interactables.EatInteraction(4) ]

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
    
)
#Palette

white = (0xFF, 0xFF, 0xFF)
black = (0x0, 0x0, 0x0)
red = (0xFF,0x0,0x0)
gray = (120,120,120)
dark_gray = (89, 89, 89)

magic_green = (164, 208, 149)
magic_purple = (79, 54, 82)
moss_green = (82, 82, 54)
monster_blue = (61, 54, 82)
monster_shine = (103, 92, 140)

stone_grey_darker = (45, 43, 42)
stone_grey_dark = (61, 58, 57)
stone_grey = (77, 73, 72)
stone_grey_light =(92, 87, 86)
stone_grey_lighter = (107, 101, 100)


bone_light = (221, 210, 178)

earth_light = (71, 53, 49)
earth_dark = (40, 30, 28)
wood_light = (62, 43, 39)
wood_dark = (34, 24, 21)

# tiles
floor_light = earth_light
floor_dark = earth_dark
wall_light = wood_light
wall_dark = wood_dark

# floor_light = stone_grey_light
# floor_dark = stone_grey_dark
# wall_light = stone_grey
# wall_dark = stone_grey_darker

#messages
player_atk = (0xE0, 0xE0, 0xE0)
enemy_atk = (0xFF, 0xC0, 0xC0)
needs_target = (0x3F, 0xFF, 0xFF)
status_effect_applied = (0x3F, 0xFF, 0x3F)
descend = (0x9F, 0x3F, 0xFF)

player_die = (0xFF, 0x30, 0x30)
enemy_die = (0xFF, 0xA0, 0x30)

welcome_text = (0x20, 0xA0, 0xFF)
health_recovered = (0x0, 0xFF, 0x0)

#bars
bar_text = white
bar_filled = (0x0, 0x60, 0x0)
bar_empty = (0x40, 0x10, 0x10)

#interface
menu_title = (255, 255, 63)
menu_text = white



interface_highlight = bone_light
interface_lowlight = moss_green

menu_selected = interface_highlight
menu_border = interface_lowlight

button_color = interface_highlight
button_hover = white
button_grey = dark_gray
button_text = interface_highlight

invalid = (0xFF, 0xFF, 0x00)
impossible = (0x80, 0x80, 0x80)
error = (0xFF, 0x40, 0x40)
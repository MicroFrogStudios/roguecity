from typing import Tuple
import enums.color as color
import numpy as np  # type: ignore

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", bool),  # True if this tile can be walked over.
        ("transparent", bool),  # True if this tile doesn't block FOV.
        ("dark", graphic_dt),  # Graphics for when this tile is not in FOV.
        ("light", graphic_dt),  # Graphics for when the tile is in FOV.
    ]
)


def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types """
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)

def grate_gate(light_fg = color.floor_light,light_bg = color.wall_light,dark_fg =color.floor_dark,dark_bg = color.wall_dark):
    return new_tile(walkable=False, transparent=True,
        dark=(ord("╪"), dark_bg, dark_fg),
        light=(ord("╪"), light_bg, light_fg))

def gate_border(light_fg = color.floor_light,light_bg = color.wall_light,dark_fg =color.floor_dark,dark_bg = color.wall_dark):
    return new_tile(walkable=False, transparent=False,
        dark=(ord("▓"), dark_bg, dark_fg),
        light=(ord("▓"), light_bg, light_fg))

def new_floor(light_color = color.floor_light, dark_color =color.floor_dark):
    return new_tile(
        walkable=True, transparent=True,
        dark=(ord(" "), (255, 255, 255), dark_color), 
        light=(ord(" "), (255, 255, 255), light_color),
    )
# versions of this method with color constants, might want to leave presets with some colors for reusing memory


def new_wall(light_color = color.wall_light, dark_color =color.wall_dark):
    return new_tile(
        walkable=False, transparent=False, 
        dark=(ord(" "), (255, 255, 255), dark_color),
        light=(ord(" "), (255, 255, 255), light_color),
    )

def new_door(light_fg = color.floor_light,light_bg = color.wall_light,dark_fg =color.floor_dark,dark_bg = color.wall_dark):
    return new_tile(walkable=True, transparent=False,
        dark=(ord("┼"), dark_bg, dark_fg),
        light=(ord("┼"), light_bg, light_fg))

down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), (0, 0, 100), (50, 50, 150)),
    light=(ord(">"), (255, 255, 255), (200, 180, 50)),
)

# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt)

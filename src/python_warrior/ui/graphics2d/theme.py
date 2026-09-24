"""Colors, sizes and fonts of the 2D view."""

import pygame

WINDOW_SIZE = (1200, 780)
FPS = 60

BACKGROUND = (22, 24, 33)
PANEL = (32, 35, 48)
PANEL_BORDER = (58, 63, 84)
TEXT = (226, 229, 240)
TEXT_DIM = (140, 146, 170)
ACCENT = (242, 184, 75)
ACCENT_DARK = (160, 112, 30)

FLOOR_A = (74, 70, 64)
FLOOR_B = (82, 78, 71)
FLOOR_LINE = (60, 57, 52)
WALL = (46, 40, 38)
WALL_BRICK = (92, 64, 52)
WALL_MORTAR = (36, 30, 28)
STAIRS = (214, 170, 82)
STAIRS_DARK = (150, 110, 46)

HP_GOOD = (92, 200, 110)
HP_MID = (234, 196, 70)
HP_LOW = (226, 80, 70)
HP_BACK = (30, 30, 36)

DAMAGE = (255, 96, 86)
HEAL = (120, 230, 140)
FIRE = (255, 150, 40)
CHAIN = (170, 174, 186)

BUTTON = (52, 57, 78)
BUTTON_HOVER = (70, 77, 104)
BUTTON_ACTIVE = (242, 184, 75)

UNIT_COLORS = {
    "Warrior": (72, 132, 240),
    "Golem": (150, 112, 78),
    "Sludge": (110, 190, 80),
    "ThickSludge": (54, 128, 60),
    "Archer": (176, 70, 60),
    "Wizard": (140, 90, 210),
    "Captive": (222, 200, 164),
}

LOG_COLORS = {
    "turn": ACCENT,
    "damage": (240, 130, 120),
    "heal": HEAL,
    "success": (130, 220, 150),
    "failure": (250, 110, 100),
    "info": TEXT,
}

_fonts = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.Font(None, size)
        _fonts[key].set_bold(bold)
    return _fonts[key]


def clear_fonts():
    """Fonts become invalid once pygame quits."""
    _fonts.clear()

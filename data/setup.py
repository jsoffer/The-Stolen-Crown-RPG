"""

This module initializes the display and
creates dictionaries of resources.

"""

__author__ = 'justinarmstrong'

SCREEN = None
SCREEN_RECT = None

FONTS = None
MUSIC = None
GFX = None
SFX = None
TMX = None
FONT = None

def register_screen(_screen):
    global SCREEN
    SCREEN = _screen

def register_screen_rect(_screen_rect):
    global SCREEN_RECT
    SCREEN_RECT = _screen_rect

def register_fonts(_fonts):
    global FONTS
    FONTS = _fonts

def register_music(_music):
    global MUSIC
    MUSIC = _music

def register_gfx(_gfx):
    global GFX
    GFX = _gfx

def register_sfx(_sfx):
    global SFX
    SFX = _sfx

def register_tmx(_tmx):
    global TMX
    TMX = _tmx

def register_font(_font):
    global FONT
    FONT = _font

def screen():
    return SCREEN

def screen_rect():
    return SCREEN_RECT

def fonts():
    return FONTS

def music():
    return MUSIC

def gfx():
    return GFX

def sfx():
    return SFX

def tmx():
    return TMX

def font():
    return FONT

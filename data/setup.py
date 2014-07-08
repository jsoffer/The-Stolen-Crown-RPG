"""

This module initializes the display and
creates dictionaries of resources.

"""

__author__ = 'justinarmstrong'

import pygame as pg

SCREEN = None
SCREEN_RECT = None

FONTS = None
GFX = None
SFX = None
TMX = None
FONT = None

KEYS = None
GAME_DATA = None

MIXER = None

def register_mixer(_mixer):
    global MIXER
    MIXER = _mixer

def update_keys():
    global KEYS
    KEYS = pg.key.get_pressed()

def keys():
    return KEYS

def register_game_data(_game_data):
    global GAME_DATA
    GAME_DATA = _game_data

def game_data():
    return GAME_DATA

def register_screen(_screen):
    global SCREEN
    SCREEN = _screen

def register_screen_rect(_screen_rect):
    global SCREEN_RECT
    SCREEN_RECT = _screen_rect

def register_fonts(_fonts):
    global FONTS
    FONTS = _fonts

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

def mixer():
    return MIXER

def gfx():
    return GFX

def sfx():
    return SFX

def tmx():
    return TMX

def font():
    return FONT

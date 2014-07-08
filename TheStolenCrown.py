#!/usr/bin/env python

"""

This is a fantasy RPG game about a warrior whose
quest is to recover a magic crown

"""

__author__ = 'justinarmstrong'

import os
import sys
import pygame as pg
from data.main import main
from data.constants import ORIGINAL_CAPTION

import data.setup as setup

def load_all_gfx(directory,
                 colorkey=(255, 0, 255),
                 accept=('.png', 'jpg', 'bmp')):
    graphics = {}
    for pic in os.listdir(directory):
        name, ext = os.path.splitext(pic)
        if ext.lower() in accept:
            img = pg.image.load(os.path.join(directory, pic))
            if img.get_alpha():
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey(colorkey)
            graphics[name] = img
    return graphics

class Mixer(object):
    """
    remote for handling pygame.mixer globally instead of keeping local state
    scattered everywhere

    """

    def __init__(self):
        self.old_song = None
        self.song_map = load_resources(
            os.path.join('resources', 'music'),
            accept=('.wav', '.mp3', '.ogg', '.mdi'))
        self.level_map = {}

    def set_level_song(self, level, song):
        self.level_map[level] = song

    def play(self, level, volume=0.4):
        song = self.level_map[level]
        if song != self.old_song:
            self.old_song = song
            pg.mixer.music.load(self.song_map[song])
            pg.mixer.music.set_volume(volume)
            pg.mixer.music.play(-1)

def load_resources(directory, accept):
    resources = {}
    for resource in os.listdir(directory):
        name, ext = os.path.splitext(resource)
        if ext.lower() in accept:
            resources[name] = os.path.join(directory, resource)
    return resources

def load_all_sfx(directory, accept=('.wav', '.mp3', '.ogg', '.mdi')):
    effects = {}
    for sound_fx in os.listdir(directory):
        name, ext = os.path.splitext(sound_fx)
        if ext.lower() in accept:
            effects[name] = pg.mixer.Sound(os.path.join(directory, sound_fx))
    return effects

if __name__ == '__main__':

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])
    pg.display.set_caption(ORIGINAL_CAPTION)

    SCREEN = pg.display.set_mode((800, 608))
    setup.register_screen(SCREEN)

    SCREEN_RECT = SCREEN.get_rect()
    setup.register_screen_rect(SCREEN_RECT)

    FONTS = load_resources(os.path.join('resources', 'fonts'),
                           accept=('.ttf'))
    setup.register_fonts(FONTS)

    TMX = load_resources(os.path.join('resources', 'tmx'),
                         accept=('.tmx'))
    setup.register_tmx(TMX)

    GFX = load_all_gfx(os.path.join('resources', 'graphics'))
    setup.register_gfx(GFX)

    SFX = load_all_sfx(os.path.join('resources', 'sound'))
    setup.register_sfx(SFX)

    FONT = pg.font.Font(FONTS['Fixedsys500c'], 20)
    setup.register_font(FONT)

    MIXER = Mixer()
    setup.register_mixer(MIXER)

    main()
    pg.quit()
    sys.exit()

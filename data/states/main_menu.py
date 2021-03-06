import pickle, os
import pygame as pg
from .. import setup, tools, tilerender
from .. import observer
from .. import constants as c
from . import death

from .levels import make_viewport

class Menu(tools.State):
    def __init__(self):
        super(Menu, self).__init__()

        self.name = c.MAIN_MENU

        self.title_rect = None
        self.title_box = None
        self.map_rect = None
        self.viewport = None
        self.map_image = None
        self.level_surface = None
        self.alpha = None
        self.state_dict = None
        self.renderer = None

        setup.mixer().set_level_song(self.name, 'kings_theme')
        self.next = c.INSTRUCTIONS
        self.tmx_map = setup.tmx()['title']
        self.name = c.MAIN_MENU
        self.startup()

    def startup(self):
        self.renderer = tilerender.Renderer(self.tmx_map)
        self.map_image = self.renderer.make_2x_map()
        self.map_rect = self.map_image.get_rect()
        self.viewport = make_viewport(self.map_image)
        self.level_surface = pg.Surface(self.map_rect.size)
        self.title_box = setup.gfx()['title_box']
        self.title_rect = self.title_box.get_rect()
        self.title_rect.midbottom = self.viewport.midbottom
        self.title_rect.y -= 30
        self.state_dict = self.make_state_dict()
        self.state = c.TRANSITION_IN
        self.alpha = 255

        #self.transition_surface = pg.Surface(setup.screen_rect().size)
        #self.transition_surface.fill(c.BLACK_BLUE)
        #self.transition_surface.set_alpha(self.alpha)

    def update(self):
        """
        Update scene.
        """
        update_level = self.state_dict[self.state]
        update_level()
        self.draw_level()

    def draw_level(self):
        """
        Blit tmx map and title box onto screen.
        """

        surface = setup.screen()

        self.level_surface.blit(self.map_image, self.viewport, self.viewport)
        self.level_surface.blit(self.title_box, self.title_rect)
        surface.blit(self.level_surface, (0, 0), self.viewport)

        #surface.blit(self.transition_surface, (0, 0))

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            self.state = c.TRANSITION_OUT

    def normal_update(self):
        pass


class Instructions(tools.State):
    """
    Instructions page.
    """
    def __init__(self):
        super(Instructions, self).__init__()

        self.name = c.INSTRUCTIONS

        self.title_rect = None
        self.title_box = None
        self.map_rect = None
        self.title_rect = None
        self.level_surface = None
        self.map_image = None
        self.name = None
        self.state_dict = None
        self.observers = None
        self.viewport = None
        self.alpha = None
        self.renderer = None

        self.tmx_map = setup.tmx()['title']

        setup.mixer().set_level_song(self.name, 'kings_theme')


    def startup(self):
        self.renderer = tilerender.Renderer(self.tmx_map)
        self.map_image = self.renderer.make_2x_map()
        self.map_rect = self.map_image.get_rect()
        self.viewport = make_viewport(self.map_image)
        self.level_surface = pg.Surface(self.map_rect.size)
        self.title_box = self.set_image()
        self.title_rect = self.title_box.get_rect()
        self.title_rect.midbottom = self.viewport.midbottom
        self.title_rect.y -= 30

        # it's registered on 'setup' by create_game_data_dict
        tools.create_game_data_dict()

        self.next = set_next_scene()
        self.state_dict = self.make_state_dict()
        self.name = c.MAIN_MENU
        self.state = c.TRANSITION_IN
        self.alpha = 255
        self.observers = [observer.SoundEffects()]

    def notify(self, event):
        """
        Notify all observers of event.
        """
        for listener in self.observers:
            listener.on_notify(event)

    def set_image(self):
        """
        Set image for message box.
        """
        return setup.gfx()['instructions_box']

    def update(self):
        """
        Update scene.
        """
        update_level = self.state_dict[self.state]
        update_level()
        self.draw_level()

    def draw_level(self):
        """
        Blit tmx map and title box onto screen.
        """

        surface = setup.screen()

        self.level_surface.blit(self.map_image, self.viewport, self.viewport)
        self.level_surface.blit(self.title_box, self.title_rect)
        self.draw_arrow()
        surface.blit(self.level_surface, (0, 0), self.viewport)
        #surface.blit(self.transition_surface, (0, 0))

    def draw_arrow(self):
        pass

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            self.state = c.TRANSITION_OUT

    def normal_update(self):
        pass

def set_next_scene():
    """
    Check if there is a saved game. If not, start
    game at begining.  Otherwise go to load game scene.

    Was a method of Instructions; uses no 'self'

    """
    if not os.path.isfile("save.p"):
        next_scene = c.OVERWORLD
    else:
        next_scene = c.LOADGAME

    return next_scene


class LoadGame(Instructions):
    def __init__(self):
        super(LoadGame, self).__init__()
        self.arrow = death.Arrow(200, 260)
        self.arrow.pos_list[1] += 34
        self.allow_input = False

    def set_image(self):
        """
        Set image for message box.
        """
        return setup.gfx()['loadgamebox']

    def draw_arrow(self):
        self.level_surface.blit(self.arrow.image, self.arrow.rect)

    def get_event(self, event):
        pass

    def normal_update(self):

        keys = setup.keys()

        if self.allow_input:
            if keys[pg.K_DOWN] and self.arrow.index == 0:
                self.arrow.index = 1
                self.notify(c.CLICK)
                self.allow_input = False
            elif keys[pg.K_UP] and self.arrow.index == 1:
                self.arrow.index = 0
                self.notify(c.CLICK)
                self.allow_input = False
            elif keys[pg.K_SPACE]:
                if self.arrow.index == 0:

                    with open("save.p", "rb") as save_file:
                        setup.register_game_data(pickle.load(save_file))

                    self.next = c.TOWN
                    self.state = c.TRANSITION_OUT
                else:
                    self.next = c.OVERWORLD
                    self.state = c.TRANSITION_OUT
                self.notify(c.CLICK2)

            self.arrow.rect.y = self.arrow.pos_list[self.arrow.index]

        if not keys[pg.K_DOWN] and not keys[pg.K_UP]:
            self.allow_input = True


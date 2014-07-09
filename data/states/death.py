"""

Game Over / 'Restart from last save point?' pseudo-"room"

"""

import pickle, os
import pygame as pg
from .. import setup, tools
from .. import observer
from ..components import person
from .. import constants as c

class Arrow(pg.sprite.Sprite):
    """
    Arrow to select restart or saved gamed.
    """
    def __init__(self, pos_x, pos_y):
        super(Arrow, self).__init__()
        self.image = setup.GFX['smallarrow']
        self.rect = self.image.get_rect(x=pos_x, y=pos_y)
        self.index = 0
        self.pos_list = [pos_y, pos_y+34]
        self.allow_input = False
        self.observers = [observer.SoundEffects()]

    def notify(self, event):
        """
        Notify all observers of event.
        """

        for listener in self.observers:
            listener.on_notify(event)

    def update(self):
        """
        Update arrow position.
        """

        keys = setup.keys()

        if self.allow_input:
            if (
                    keys[pg.K_DOWN] and
                    not keys[pg.K_UP] and
                    self.index == 0):
                self.index = 1
                self.allow_input = False
                self.notify(c.CLICK)
            elif (keys[pg.K_UP] and
                  not keys[pg.K_DOWN] and
                  self.index == 1):
                self.index = 0
                self.allow_input = False
                self.notify(c.CLICK)

            self.rect.y = self.pos_list[self.index]

        if not keys[pg.K_DOWN] and not keys[pg.K_UP]:
            self.allow_input = True

class DeathScene(tools.State):
    """
    Scene when the player has died.
    """
    def __init__(self):
        super(DeathScene, self).__init__()

        self.name = c.DEATH_SCENE

        self.arrow = None
        self.alpha = None
        self.observers = None
        self.message_box = None
        self.background = None
        self.font = None
        self.player = None
        self.state_dict = None

        self.next = c.TOWN
        setup.mixer().set_level_song(self.name, 'shop_theme')

    def startup(self):
        self.font = pg.font.Font(setup.FONTS[c.MAIN_FONT], 22)
        self.background = pg.Surface(setup.SCREEN_RECT.size)
        self.background.fill(c.BLACK_BLUE)
        self.player = person.Player('down', 1, 1, 'resting', 1)
        self.player.image = pg.transform.scale2x(self.player.image)
        self.player.rect = self.player.image.get_rect()
        self.player.rect.center = setup.SCREEN_RECT.center
        self.message_box = self.make_message_box()
        self.arrow = Arrow(300, 532)
        self.state_dict = self.make_state_dict()
        self.state = c.TRANSITION_IN
        self.alpha = 255
        if not os.path.isfile("save.p"):
            # initializes setup.game_data internally
            tools.create_game_data_dict()
            with open("save.p", "wb") as save_file:
                pickle.dump(game_data, save_file)
        self.observers = [observer.SoundEffects()]

    def notify(self, event):
        """
        Notify all observers of event.
        """
        for listener in self.observers:
            listener.on_notify(event)

    def make_message_box(self):
        """
        Make the text box informing of death.
        """
        box_image = setup.GFX['dialoguebox']
        box_rect = box_image.get_rect()
        text = 'You have died. Restart from last save point?'
        text_render = self.font.render(text, True, c.NEAR_BLACK)
        text_rect = text_render.get_rect(centerx=box_rect.centerx,
                                         y=30)
        text2 = 'Yes'
        text2_render = self.font.render(text2, True, c.NEAR_BLACK)
        text2_rect = text2_render.get_rect(centerx=box_rect.centerx,
                                           y=70)

        text3 = 'No'
        text3_render = self.font.render(text3, True, c.NEAR_BLACK)
        text3_rect = text3_render.get_rect(centerx=box_rect.centerx,
                                           y=105)

        temp_surf = pg.Surface(box_rect.size)
        temp_surf.set_colorkey(c.BLACK)
        temp_surf.blit(box_image, box_rect)
        temp_surf.blit(text_render, text_rect)
        temp_surf.blit(text2_render, text2_rect)
        temp_surf.blit(text3_render, text3_rect)

        box_sprite = pg.sprite.Sprite()
        box_sprite.image = temp_surf
        box_sprite.rect = temp_surf.get_rect(bottom=608)

        return box_sprite

    def update(self):
        """
        Update scene.
        """
        update_level = self.state_dict[self.state]
        update_level()
        self.draw_level()

    def normal_update(self):
        self.arrow.update()
        self.check_for_input()

    def check_for_input(self):
        """
        Check if player wants to restart from last save point
        or just start from the beginning of the game.
        """

        keys = setup.keys()

        if keys[pg.K_SPACE]:
            if self.arrow.index == 0:
                self.next = c.TOWN
                with open("save.p", "rb") as save_file:
                    setup.register_game_data(pickle.load(save_file))
            elif self.arrow.index == 1:
                self.next = c.MAIN_MENU
            self.state = c.TRANSITION_OUT
            self.notify(c.CLICK2)

    def draw_level(self):
        """
        Draw background, player, and message box.
        """

        surface = setup.screen()

        surface.blit(self.background, (0, 0))
        surface.blit(self.player.image, self.player.rect)
        surface.blit(self.message_box.image, self.message_box.rect)
        surface.blit(self.arrow.image, self.arrow.rect)
        surface.blit(self.transition_surface, (0, 0))

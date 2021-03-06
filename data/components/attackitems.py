"""
Attack equipment for battles.
"""
import copy
import pygame as pg
from .. import tools, setup
from .. import constants as c


class Sword(object):
    """
    Sword that appears during regular attacks.
    """
    def __init__(self, player):
        self.player = player
        self.sprite_sheet = setup.gfx()['shopsigns']
        self.image_list = self.make_image_list()
        self.index = 0
        self.timer = tools.Timer(60)

    def make_image_list(self):
        """
        Make the list of two images for animation.
        """
        image_list = [tools.get_image(48, 0, 16, 16, self.sprite_sheet),
                      tools.get_image(0, 0, 22, 16, setup.gfx()['sword2'])]
        return image_list

    @property
    def image(self):
        new_image = self.image_list[self.index]
        return pg.transform.scale2x(new_image)

    @property
    def rect(self):
        new_rect = copy.copy(self.player.rect)
        new_rect.bottom += 17
        new_rect.right -= 16
        return new_rect

    def update(self):
        if self.timer.done():
            if self.index == 0:
                self.index += 1
            else:
                self.index -= 1
            self.timer.reset()

    def draw(self):
        """
        Draw sprite to surface.
        """
        if self.player.state == 'attack':
            surface = setup.screen()
            surface.blit(self.image, self.rect)

class HealthPoints(pg.sprite.Sprite):
    """
    A sprite that shows how much damage an attack inflicted.
    """
    def __init__(self, points, topleft_pos, damage=True, ether=False):
        super(HealthPoints, self).__init__()

        self.font = pg.font.Font(setup.fonts()[c.MAIN_FONT], 27)

        self.text_image = self.make_surface(points, damage, ether)
        self.rect = self.text_image.get_rect(x=topleft_pos[0]+20,
                                             bottom=topleft_pos[1]+10)

        self.image = tools.FadeSurface(self.rect.size)

        self.image.blit(self.text_image, (0, 0))

        self.start_posy = self.rect.y
        self.y_vel = -1

    def make_surface(self, points, damage, ether):
        """
        Make the surface for the sprite.
        """
        if damage:
            if points > 0:
                text = "-{}".format(str(points))
                surface = self.font.render(text, True, c.RED)
                return surface
            else:
                return self.font.render('Miss', True, c.WHITE).convert_alpha()
        else:
            text = "+{}".format(str(points))
            if ether:
                surface = self.font.render(text, True, c.PINK)
            else:
                surface = self.font.render(text, True, c.GREEN)

            return surface

    def update(self):
        """
        Update sprite position or delete if necessary.
        """
        self.rect.y += self.y_vel
        if self.rect.y < (self.start_posy - 29):
            self.fade_animation()

    def fade_animation(self):
        """
        Fade score in and out.
        """
        self.image.update_alpha(15)
        if self.image.faded():
            self.kill()

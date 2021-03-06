"""

Store and show attribution

"""

import pygame as pg
from .. import tools, setup
from .. import constants as c


class CreditEntry(object):
    """
    The text for each credit for the game.
    """
    def __init__(self, level):

        self.alpha = 0
        self.font = pg.font.Font(setup.fonts()[c.MAIN_FONT], 22)
        self.credit_sprites = self.make_credits()
        self.index = 0
        self.current_credit = self.credit_sprites[self.index]
        self.state_dict = {c.TRANSITION_IN: self.transition_in,
                           c.TRANSITION_OUT: self.transition_out,
                           c.NORMAL: self.normal_update}
        self.state = c.TRANSITION_IN
        self.transition_timer = tools.Timer(4500)
        self.level = level

    def make_credits(self):
        """
        Make a list of lists for all the credit surfaces.
        """
        sc_credits = [['THE STOLEN CROWN', 'A Fantasy RPG'],
                      ['PROGRAMMING AND GAME DESIGN', 'Justin Armstrong'],
                      ['ART', 'JPhilipp',
                       'Reemax',
                       'Lanea Zimmerman',
                       'Redshrike',
                       'StumpyStrust',
                       'Benjamin Larsson',
                       'russpuppy',
                       'hc',
                       'Iron Star Media'],
                      ['MUSIC', 'Telaron: The King\'s Theme',
                       'Mekathratos: Forest Dance (Town Theme)',
                       'bart: Adventure Begins (Overworld Theme)',
                       '8th Mode Music: High Action (Battle Theme)',
                       'Arron Krogh: Coastal Town (Shop Theme)',
                       'Arron Krogh: My Enemy (Dungeon Theme)',
                       'Matthew Pablo: Enchanted Festival (Victory Theme)',
                       'Matthew Pablo: Pleasant Creek (Brother Theme)'],
                      ['SOUND EFFECTS', 'Kenney',
                       'Nic3_one',
                       'Ekokubza123',
                       'kuzyaburst',
                       'audione'],
                      ['SPECIAL THANKS', '/r/pygame',
                       'Leif Theden',
                       'Stacey Hunniford']]

        credit_sprites = []

        for credit in sc_credits:
            subcredit_list = []
            for i, subcredit in enumerate(credit):
                text_sprite = pg.sprite.Sprite()
                text_sprite.text_image = self.font.render(
                    subcredit, True, c.WHITE)
                text_sprite.rect = text_sprite.text_image.get_rect(
                    centerx=400, y=100+(i*40))
                text_sprite.image = pg.Surface(text_sprite.rect.size).convert()
                text_sprite.image.set_colorkey(c.BLACK)
                text_sprite.image.set_alpha(self.alpha)
                subcredit_list.append(text_sprite)
            credit_sprites.append(subcredit_list)

        return credit_sprites

    def transition_in(self):
        for credit in self.current_credit:
            credit.image = pg.Surface(credit.rect.size).convert()
            credit.image.set_colorkey(c.BLACK)
            credit.image.set_alpha(self.alpha)
            credit.image.blit(credit.text_image, (0, 0))

        self.alpha += 5
        if self.alpha >= 255:
            self.alpha = 255
            self.state = c.NORMAL

    def transition_out(self):
        for credit in self.current_credit:
            credit.image = pg.Surface(credit.rect.size).convert()
            credit.image.set_colorkey(c.BLACK)
            credit.image.set_alpha(self.alpha)
            credit.image.blit(credit.text_image, (0, 0))

        self.alpha -= 5
        if self.alpha <= 0:
            self.alpha = 0
            if self.index < len(self.credit_sprites) - 1:
                self.index += 1
            else:
                self.level.done = True
                self.level.next = c.MAIN_MENU
            self.current_credit = self.credit_sprites[self.index]
            self.state = c.TRANSITION_IN

    def normal_update(self):
        if self.transition_timer.done():
            self.state = c.TRANSITION_OUT
            self.transition_timer.reset()

    def update(self):
        update_method = self.state_dict[self.state]
        update_method()

    def draw(self):
        """
        Draw the current credit to main surface.
        """
        surface = setup.screen()

        for credit_sprite in self.current_credit:
            surface.blit(credit_sprite.image, credit_sprite.rect)


class Credits(tools.State):
    """
    End Credits Scene.
    """
    def __init__(self):
        super(Credits, self).__init__()
        self.name = c.CREDITS

        setup.mixer().set_level_song(self.name, None)

        self.credit = None
        self.background = None

    def startup(self):
        """
        Initialize data at scene start.
        """

        self.background = pg.Surface(setup.screen_rect().size)
        self.background.fill(c.BLACK_BLUE)
        self.credit = CreditEntry(self)

    def update(self):
        """
        Update scene.
        """
        self.credit.update()
        self.draw_scene()

    def draw_scene(self):
        """
        Draw all graphics to the window surface.
        """

        surface = setup.screen()

        surface.blit(self.background, (0, 0))
        self.credit.draw()




"""
This is the state where the player can look at
his inventory, equip items and check stats.
Most of the logic is in menugui.MenuGUI()

"""
from .. import tools, menugui
from .. import setup
from .. import constants as c


class PlayerMenu(tools.State):
    def __init__(self, level):
        super(PlayerMenu, self).__init__()

        self.name = c.PLAYER_MENU

        game_data = setup.game_data()

        inventory = game_data['player inventory']
        stats = game_data['player stats']

        self.get_image = tools.get_image
        self.allow_input = False
        self.background = self.make_background()
        self.gui = menugui.MenuGui(level, inventory, stats)

    def make_background(self):
        """
        Makes the generic black/blue background.
        """
        background = tools.empty_background()

        player = self.make_sprite('player', (96, 32), (30, 40), resize=150)

        background.image.blit(player.image, player.rect)

        return background

    def update(self):
        self.gui.update()
        self.draw()

    def draw(self):

        surface = setup.screen()

        surface.blit(self.background.image, self.background.rect)
        self.gui.draw()


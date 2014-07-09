"""
This class is the parent class of all shop states.
This includes weapon, armour, magic and potion shops.
It also includes the inn.  These states are scaled
twice as big as a level state. The self.gui controls
all the textboxes.
"""

import copy
import pygame as pg
from .. import tools, setup, shopgui
from .. import constants as c


class Shop(tools.State):
    """Basic shop state"""
    def __init__(self):
        super(Shop, self).__init__()

        self.keeper = None

        self.dialogue = {}

        self.items = None
        self.sell_items = None

        self.state_dict = None
        self.gui = None
        self.background = None

    def startup(self):
        """Startup state"""
        self.state_dict = self.make_state_dict()
        self.state = 'transition in'
        self.next = c.TOWN
        self.dialogue['dialogue'] = self.make_dialogue()
        self.dialogue['accept'] = self.make_accept_dialogue()
        self.dialogue['accept sale'] = ['Item sold.']
        self.items = setup.yaml()[self.name]
        self.background = self.make_background()
        self.gui = shopgui.Gui(self)

        setup.mixer().set_level_song(self.name, 'shop_theme')

    def make_dialogue(self):
        """
        Make the list of dialogue phrases.
        """
        raise NotImplementedError

    def make_accept_dialogue(self):
        """
        Make the dialogue for when the player buys an item.
        """
        return ['Item purchased.']

    def make_purchasable_items(self):
        """
        Make the list of items to be bought at shop.
        """
        raise NotImplementedError

    def make_background(self):
        """
        Make the level surface.
        """
        background = tools.empty_background()

        player = self.make_sprite(
            'player', (96, 32), (150, 200), resize=200)
        shop_owner = self.make_sprite(
            self.keeper, (32, 32), (600, 200), resize=200)
        counter = self.make_counter()

        background.image.blit(player.image, player.rect)
        background.image.blit(shop_owner.image, shop_owner.rect)
        background.image.blit(counter.image, counter.rect)

        return background

    def make_counter(self):
        """
        Make the counter to conduct business.
        """
        sprite_sheet = copy.copy(setup.gfx()['house'])
        sprite = pg.sprite.Sprite()
        sprite.image = tools.get_image(102, 64, 26, 82, sprite_sheet)
        sprite.image = pg.transform.scale2x(sprite.image)
        sprite.rect = sprite.image.get_rect(left=550, top=225)

        return sprite

    def update(self):
        """
        Update scene.
        """

        state_function = self.state_dict[self.state]
        state_function()

    def normal_update(self):
        """
        Update level normally.
        """
        self.gui.update()
        self.draw_level()

    def draw_level(self):
        """
        Blit graphics to game surface.
        """

        surface = setup.screen()

        surface.blit(self.background.image, self.background.rect)
        self.gui.draw()


class Inn(Shop):
    """
    Where our hero gets rest.
    """
    def __init__(self):
        super(Inn, self).__init__()
        self.name = c.INN
        self.keeper = 'innman'

    def make_dialogue(self):
        """
        Make the list of dialogue phrases.
        """
        return ["Welcome to the " + self.name + "!",
                "Would you like a room to restore your health?"]

    def make_accept_dialogue(self):
        """
        Make the dialogue for when the player buys an item.
        """
        return ['Your health has been replenished and your game saved!']

class WeaponShop(Shop):
    """A place to buy weapons"""
    def __init__(self):
        super(WeaponShop, self).__init__()
        self.name = c.WEAPON_SHOP
        self.keeper = 'weaponman'
        self.sell_items = ['Long Sword', 'Rapier']


    def make_dialogue(self):
        """Make the list of dialogue phrases"""
        shop_name = "{}{}".format(self.name[0].upper(), self.name[1:])
        return ["Welcome to the " + shop_name + "!",
                "What weapon would you like to buy?"]

class ArmorShop(Shop):
    """A place to buy armor"""
    def __init__(self):
        super(ArmorShop, self).__init__()
        self.name = c.ARMOR_SHOP
        self.keeper = 'armorman'
        self.sell_items = ['Chain Mail', 'Wooden Shield']


    def make_dialogue(self):
        """Make the list of dialogue phrases"""
        shop_name = "{}{}".format(self.name[0].upper(), self.name[1:])
        return ["Welcome to the " + shop_name + "!",
                "Would piece of armor would you like to buy?"]


class MagicShop(Shop):
    """A place to buy magic"""
    def __init__(self):
        super(MagicShop, self).__init__()
        self.name = c.MAGIC_SHOP
        self.keeper = 'magiclady'


    def make_dialogue(self):
        """Make the list of dialogue phrases"""
        shop_name = "{}{}".format(self.name[0].upper(), self.name[1:])
        return ["Welcome to the " + shop_name + "!",
                "Would magic spell would you like to buy?"]


class PotionShop(Shop):
    """A place to buy potions"""
    def __init__(self):
        super(PotionShop, self).__init__()
        self.name = c.POTION_SHOP
        self.keeper = 'potionlady'
        self.sell_items = ['Healing Potion', 'Ether Potion']


    def make_dialogue(self):
        """Make the list of dialogue phrases"""
        shop_name = "{}{}".format(self.name[0].upper(), self.name[1:])
        return ["Welcome to the " + shop_name + "!",
                "What potion would you like to buy?"]

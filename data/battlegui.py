"""
GUI components for battle states.
"""

import pygame as pg
from . import setup, observer
from . import constants as c

class InfoBox(object):
    """
    Info box that describes attack damage and other battle
    related information.
    """
    def __init__(self, experience, gold):
        self.enemy_damage = 0
        self.player_damage = 0
        self.state = c.SELECT_ACTION
        self.title_font = pg.font.Font(setup.fonts()[c.MAIN_FONT], 22)
        self.title_font.set_underline(True)
        self.font = pg.font.Font(setup.fonts()[c.MAIN_FONT], 18)
        self.experience_points = experience
        self.gold_earned = gold
        self.state_dict = self.make_state_dict()
        self.image = self.make_image()
        self.rect = self.image.get_rect(bottom=608)
        self.item_text_list = self.make_item_text()[1:]
        self.magic_text_list = self.make_magic_text()[1:]

    def make_state_dict(self):
        """
        Make dictionary of states Battle info can be in.
        """
        state_dict = {
            c.SELECT_ACTION: 'Select an action.',
            c.SELECT_MAGIC: 'Select a magic spell.',
            c.SELECT_ITEM: 'Select an item.',
            c.SELECT_ENEMY: 'Select an enemy.',
            c.ENEMY_ATTACK: 'Enemy attacks player!',
            c.PLAYER_ATTACK: 'Player attacks enemy! ',
            c.RUN_AWAY: 'RUN AWAY!!!',
            c.ENEMY_DAMAGED: self.enemy_damaged(),
            c.ENEMY_DEAD: 'Enemy killed.',
            c.PLAYER_DAMAGED: self.player_hit(),
            c.DRINK_HEALING_POTION: 'Player healed.',
            c.DRINK_ETHER_POTION: 'Magic Points Increased.',
            c.FIRE_SPELL: 'FIRE BLAST!',
            c.BATTLE_WON: 'Battle won!',
            c.SHOW_EXPERIENCE: self.show_experience(),
            c.LEVEL_UP: self.level_up(),
            c.TWO_ACTIONS: 'Two actions per turn mode is now available.',
            c.SHOW_GOLD: self.show_gold()}

        return state_dict

    def enemy_damaged(self):
        """
        Return text of enemy being hit using calculated damage.
        """
        return "Enemy hit with {} damage.".format(self.enemy_damage)

    def make_item_text(self):
        """
        Make the text for when the player selects items.
        """
        inventory = setup.game_data()['player inventory']
        allowed_item_list = ['Healing Potion', 'Ether Potion']
        title = 'SELECT ITEM'
        item_text_list = [title]

        for item in allowed_item_list:
            if item in inventory:
                text = item + ": " + str(inventory[item]['quantity'])
                item_text_list.append(text)

        item_text_list.append('BACK')

        return item_text_list

    def make_magic_text(self):
        """
        Make the text for when the player selects magic.
        """
        inventory = setup.game_data()['player inventory']
        allowed_item_list = ['Fire Blast', 'Cure']
        title = 'SELECT MAGIC SPELL'
        magic_text_list = [title]
        spell_list = [item for item in inventory if item in allowed_item_list]
        magic_text_list.extend(spell_list)
        magic_text_list.append('BACK')

        return magic_text_list

    def make_text_sprites(self, text_list):
        """
        Make sprites out of text.
        """
        sprite_group = pg.sprite.Group()

        for index, text in enumerate(text_list):
            sprite = pg.sprite.Sprite()

            if index == 0:
                pos_x = 195
                pos_y = 10
                surface = self.title_font.render(text, True, c.NEAR_BLACK)
                rect = surface.get_rect(x=pos_x, y=pos_y)
            else:
                pos_x = 100
                pos_y = (index * 30) + 20
                surface = self.font.render(text, True, c.NEAR_BLACK)
                rect = surface.get_rect(x=pos_x, y=pos_y)
            sprite.image = surface
            sprite.rect = rect
            sprite_group.add(sprite)

        return sprite_group

    def make_image(self):
        """
        Make image out of box and message.
        """
        image = setup.gfx()['shopbox']
        rect = image.get_rect(bottom=608)
        surface = pg.Surface(rect.size)
        surface.set_colorkey(c.BLACK)
        surface.blit(image, (0, 0))

        if self.state == c.SELECT_ITEM:
            text_sprites = self.make_text_sprites(self.make_item_text())
            text_sprites.draw(surface)
        elif self.state == c.SELECT_MAGIC:
            text_sprites = self.make_text_sprites(self.make_magic_text())
            text_sprites.draw(surface)
        else:
            text_surface = self.font.render(
                self.state_dict[self.state], True, c.NEAR_BLACK)
            text_rect = text_surface.get_rect(x=50, y=50)
            surface.blit(text_surface, text_rect)

        return surface

    def set_enemy_damage(self, enemy_damage):
        """
        Set enemy damage in state dictionary.
        """
        self.enemy_damage = enemy_damage
        self.state_dict[c.ENEMY_DAMAGED] = self.enemy_damaged()

    def set_player_damage(self, player_damage):
        """
        Set player damage in state dictionary.
        """
        self.player_damage = player_damage
        self.state_dict[c.PLAYER_DAMAGED] = self.player_hit()

    def player_hit(self):
        if self.player_damage:
            return "Player hit with {} damage".format(self.player_damage)
        else:
            return "Enemy missed!"

    def update(self):
        """Updates info box"""
        self.image = self.make_image()

    def show_experience(self):
        """
        Show how much experience the player earned.
        """
        return "You earned {} experience points this battle!".format(
            self.experience_points)

    def show_gold(self):
        """
        Show how much gold the player earned.
        """
        return "You found {} gold.".format(self.gold_earned)

    def level_up(self):
        """
        Return message indicating a level up for player.
        """
        return "You leveled up to Level {}!".format(
            setup.game_data()['player stats']['Level'])

    def reset_level_up_message(self):
        self.state_dict[c.LEVEL_UP] = self.level_up()



class SelectBox(object):
    """
    Box to select whether to attack, use item, use magic or run away.
    """

    def __init__(self):
        self.font = pg.font.Font(setup.fonts()[c.MAIN_FONT], 22)
        self.slots = make_slots()
        self.image = self.make_image()
        self.rect = self.image.get_rect(bottom=608,
                                        right=800)

    def make_image(self):
        """
        Make the box image for
        """
        image = setup.gfx()['goldbox']
        rect = image.get_rect(bottom=608)
        surface = pg.Surface(rect.size)
        surface.set_colorkey(c.BLACK)
        surface.blit(image, (0, 0))

        for text in self.slots:
            text_surface = self.font.render(text, True, c.NEAR_BLACK)
            text_rect = text_surface.get_rect(x=self.slots[text]['x'],
                                              y=self.slots[text]['y'])
            surface.blit(text_surface, text_rect)

        return surface

def make_slots():
    """
    Make the slots that hold the text selections, and locations.

    Was a method of SelectBox; uses no 'self'

    """

    slot_dict = {}
    selections = ['Attack', 'Items', 'Magic', 'Run']

    for i, text in enumerate(selections):
        slot_dict[text] = {'x': 150,
                           'y': (i*34)+10}

    return slot_dict


class SelectArrow(object):
    """Small arrow for menu"""
    def __init__(self, enemy_pos_list, info_box):
        self.info_box = info_box
        self.image = setup.gfx()['smallarrow']
        self.rect = self.image.get_rect()
        self.state = 'select action'
        self.state_dict = self.make_state_dict()
        self.pos_list = make_select_action_pos_list()
        self.index = 0
        self.rect.topleft = self.pos_list[self.index]
        self.allow_input = False
        self.enemy_pos_list = enemy_pos_list
        self.observers = [observer.SoundEffects()]

    def notify(self, event):
        """
        Notify all observers of events.
        """
        for listener in self.observers:
            listener.on_notify(event)

    def make_state_dict(self):
        """Make state dictionary"""
        state_dict = {'select action': self.select_action,
                      'select enemy': self.select_enemy,
                      'select item': self.select_item,
                      'select magic': self.select_magic,
                      'invisible': self.become_invisible_surface}

        return state_dict

    def select_action(self):
        """
        Select what action the player should take.
        """
        self.pos_list = make_select_action_pos_list()
        if self.index > (len(self.pos_list) - 1):
            print(self.pos_list, self.index)
        self.rect.topleft = self.pos_list[self.index]

        self.check_input()

    def select_enemy(self):
        """
        Select what enemy you want to take action on.
        """
        self.pos_list = self.enemy_pos_list

        if self.pos_list:
            pos = self.pos_list[self.index]
            self.rect.x = pos[0] - 60
            self.rect.y = pos[1] + 20

        self.check_input()

    def check_input(self):

        keys = setup.keys()

        if self.allow_input:
            if keys[pg.K_DOWN] and self.index < (len(self.pos_list) - 1):
                self.notify(c.CLICK)
                self.index += 1
                self.allow_input = False
            elif keys[pg.K_UP] and self.index > 0:
                self.notify(c.CLICK)
                self.index -= 1
                self.allow_input = False


        if keys[pg.K_DOWN] == False and keys[pg.K_UP] == False \
                and keys[pg.K_RIGHT] == False and keys[pg.K_LEFT] == False:
            self.allow_input = True

    def select_item(self):
        """
        Select item to use.
        """
        self.pos_list = self.make_select_item_pos_list()

        pos = self.pos_list[self.index]
        self.rect.x = pos[0] - 60
        self.rect.y = pos[1] + 20

        self.check_input()

    def make_select_item_pos_list(self):
        """
        Make the coordinates for the arrow for the item select screen.
        """
        pos_list = []
        text_list = self.info_box.make_item_text()
        text_list = text_list[1:]

        for i in range(len(text_list)):
            left = 90
            top = (i * 29) + 488
            pos_list.append((left, top))

        return pos_list

    def select_magic(self):
        """
        Select magic to use.
        """
        self.pos_list = self.make_select_magic_pos_list()

        pos = self.pos_list[self.index]
        self.rect.x = pos[0] - 60
        self.rect.y = pos[1] + 20

        self.check_input()

    def make_select_magic_pos_list(self):
        """
        Make the coordinates for the arrow for the magic select screen.
        """
        pos_list = []
        text_list = self.info_box.make_magic_text()
        text_list = text_list[1:]

        for i in range(len(text_list)):
            left = 90
            top = (i * 29) + 488
            pos_list.append((left, top))

        return pos_list


    def become_invisible_surface(self, *_):
        """
        Make image attribute an invisible surface.
        """
        self.image = pg.Surface(self.rect.size)
        self.image.set_colorkey(c.BLACK)

    def become_select_item_state(self):
        self.index = 0
        self.state = c.SELECT_ITEM

    def become_select_magic_state(self):
        self.index = 0
        self.state = c.SELECT_MAGIC

    def update(self):
        """
        Update arrow position.
        """
        self.image = setup.gfx()['smallarrow']
        state_function = self.state_dict[self.state]
        state_function()

    def draw(self):
        """
        Draw to surface.
        """
        surface = setup.screen()
        surface.blit(self.image, self.rect)

    def remove_pos(self, enemy):
        enemy_list = self.enemy_pos_list
        enemy_pos = list(enemy.rect.topleft)

        self.enemy_pos_list = [pos for pos in enemy_list if pos != enemy_pos]

def make_select_action_pos_list():
    """
    Make the list of positions the arrow can be in.

    Was a method of SelectArrow; uses no 'self'

    """
    pos_list = []

    for row in range(4):
        pos_x = 590
        pos_y = (row * 34) + 472
        pos_list.append((pos_x, pos_y))

    return pos_list


class PlayerHealth(object):
    """
    Basic health meter for player.
    """
    def __init__(self, select_box_rect):
        game_data = setup.game_data()
        self.health_stats = game_data['player stats']['health']
        self.magic_stats = game_data['player stats']['magic']
        self.title_font = pg.font.Font(setup.fonts()[c.MAIN_FONT], 22)
        self.posx = select_box_rect.centerx
        self.posy = select_box_rect.y - 5

    @property
    def image(self):
        """
        Make the image surface for the player
        """
        current_health = str(self.health_stats['current'])
        max_health = str(self.health_stats['maximum'])
        if len(current_health) == 2:
            buffer = '  '
        elif len(current_health) == 1:
            buffer = '    '
        else:
            buffer = ''
        health_string = "Health: {}{}/{}".format(
            buffer, current_health, max_health)
        health_surface = self.title_font.render(
            health_string, True, c.NEAR_BLACK)
        health_rect = health_surface.get_rect(x=20, y=9)

        current_magic = str(self.magic_stats['current'])
        if len(current_magic) == 2:
            buffer = '  '
        elif len(current_magic) == 1:
            buffer = '    '
        else:
            buffer = ''
        max_magic = str(self.magic_stats['maximum'])
        magic_string = "Magic:  {}{}/{}".format(
            buffer, current_magic, max_magic)
        magic_surface = self.title_font.render(
            magic_string, True, c.NEAR_BLACK)
        magic_rect = magic_surface.get_rect(x=20, top=health_rect.bottom)

        box_surface = setup.gfx()['battlestatbox']
        box_rect = box_surface.get_rect()

        parent_surface = pg.Surface(box_rect.size)
        parent_surface.blit(box_surface, box_rect)
        parent_surface.blit(health_surface, health_rect)
        parent_surface.blit(magic_surface, magic_rect)

        return parent_surface

    @property
    def rect(self):
        """
        Make the rect object for image surface.
        """
        return self.image.get_rect(centerx=self.posx, bottom=self.posy)

    def draw(self):
        """
        Draw health to surface.
        """
        surface = setup.screen()
        surface.blit(self.image, self.rect)

from __future__ import division
#from itertools import izip
import math, random, copy
import pygame as pg
from .. import setup, observer
from .. import constants as c
from ..tools import Timer, get_image

class Person(pg.sprite.Sprite):
    """
    Base class for all world characters
    controlled by the computer

    """

    def __init__(self, sheet_key, pos_x, pos_y,
                 direction='down', state='resting', index=0):
        super(Person, self).__init__()
        self.alpha = 255
        self.name = sheet_key
        self.get_image = get_image
        self.spritesheet_dict = self.create_spritesheet_dict(sheet_key)
        self.animation_dict = self.create_animation_dict()
        self.index = index
        self.direction = direction
        self.image_list = self.animation_dict[self.direction]
        self.image = self.image_list[self.index]
        self.rect = self.image.get_rect(left=pos_x, top=pos_y)
        self.origin_pos = self.rect.topleft
        self.state_dict = self.create_state_dict()

        # create_vector_dict was a no-self-use method, but couldn't
        # be separated because classes inherited from Person reimplemented
        # it, and the reimplementation was called at __init__. Now it fills
        # vector_dict internally. Not the best scheme.
        self.vector_dict = None
        self.create_vector_dict()

        self.x_vel = 0
        self.y_vel = 0
        self.state = state
        self.blockers = self.set_blockers()
        self.location = self.get_tile_location()
        self.dialogue = ['Location: ' + str(self.location)]
        self.default_direction = direction
        self.item = None
        self.wander_box = self.make_wander_box()
        self.observers = [observer.SoundEffects()]
        self.health = 0
        self.death_image = pg.transform.scale2x(self.image)
        self.battle = None

        self.anim_timer = Timer(100)
        self.move_timer = Timer(2000)

    def create_spritesheet_dict(self, sheet_key):
        """
        Make a dictionary of images from sprite sheet.
        """
        image_list = []
        image_dict = {}
        sheet = setup.gfx()[sheet_key]

        image_keys = ['facing up 1', 'facing up 2',
                      'facing down 1', 'facing down 2',
                      'facing left 1', 'facing left 2',
                      'facing right 1', 'facing right 2']

        for row in range(2):
            for column in range(4):
                image_list.append(
                    self.get_image(column*32, row*32, 32, 32, sheet))

        for key, image in zip(image_keys, image_list):
            image_dict[key] = image

        return image_dict

    def create_animation_dict(self):
        """
        Return a dictionary of image lists for animation.
        """
        image_dict = self.spritesheet_dict

        left_list = (
            [image_dict['facing left 1'], image_dict['facing left 2']])
        right_list = (
            [image_dict['facing right 1'], image_dict['facing right 2']])
        up_list = (
            [image_dict['facing up 1'], image_dict['facing up 2']])
        down_list = (
            [image_dict['facing down 1'], image_dict['facing down 2']])

        direction_dict = {'left': left_list,
                          'right': right_list,
                          'up': up_list,
                          'down': down_list}

        return direction_dict

    def create_state_dict(self):
        """
        Return a dictionary of all state methods.
        """
        state_dict = {'resting': self.resting,
                      'moving': self.moving,
                      'animated resting': self.animated_resting,
                      'autoresting': self.auto_resting,
                      'automoving': self.auto_moving,
                      'battle resting': self.battle_resting,
                      'attack': self.attack,
                      'enemy attack': self.enemy_attack,
                      c.RUN_AWAY: self.run_away,
                      c.VICTORY_DANCE: self.victory_dance,
                      c.KNOCK_BACK: self.knock_back,
                      c.FADE_DEATH: self.fade_death}

        return state_dict

    def create_vector_dict(self):
        """
        Return a dictionary of x and y velocities set to
        direction keys.
        """
        self.vector_dict = {'up': (0, -1),
                            'down': (0, 1),
                            'left': (-1, 0),
                            'right': (1, 0)}

    def update(self, unused_keys=None):
        """
        Update sprite.

        "unused_keys" is a template for derived classes

        """
        self.blockers = self.set_blockers()
        self.image_list = self.animation_dict[self.direction]
        state_function = self.state_dict[self.state]
        state_function()
        self.location = self.get_tile_location()

    def set_blockers(self):
        """
        Sets blockers to prevent collision with other sprites.
        """
        blockers = []

        if self.state == 'resting' or self.state == 'autoresting':
            blockers.append(pg.Rect(self.rect.x, self.rect.y, 32, 32))

        elif self.state == 'moving' or self.state == 'automoving':
            if self.rect.x % 32 == 0:
                tile_float = self.rect.y / float(32)
                tile1 = (self.rect.x, math.ceil(tile_float)*32)
                tile2 = (self.rect.x, math.floor(tile_float)*32)
                tile_rect1 = pg.Rect(tile1[0], tile1[1], 32, 32)
                tile_rect2 = pg.Rect(tile2[0], tile2[1], 32, 32)
                blockers.extend([tile_rect1, tile_rect2])

            elif self.rect.y % 32 == 0:
                tile_float = self.rect.x / float(32)
                tile1 = (math.ceil(tile_float)*32, self.rect.y)
                tile2 = (math.floor(tile_float)*32, self.rect.y)
                tile_rect1 = pg.Rect(tile1[0], tile1[1], 32, 32)
                tile_rect2 = pg.Rect(tile2[0], tile2[1], 32, 32)
                blockers.extend([tile_rect1, tile_rect2])

        return blockers

    def get_tile_location(self):
        """
        Convert pygame coordinates into tile coordinates.
        """
        if self.rect.x == 0:
            tile_x = 0
        elif self.rect.x % 32 == 0:
            tile_x = (self.rect.x / 32)
        else:
            tile_x = 0

        if self.rect.y == 0:
            tile_y = 0
        elif self.rect.y % 32 == 0:
            tile_y = (self.rect.y / 32)
        else:
            tile_y = 0

        return [tile_x, tile_y]


    def make_wander_box(self):
        """
        Make a list of rects that surround the initial location
        of a sprite to limit his/her wandering.
        """

        tile_x = int(self.location[0])
        tile_y = int(self.location[1])
        box_list = []
        box_rects = []

        for i in range(tile_x - 3, tile_x + 4):
            box_list.append([i, tile_y - 3])
            box_list.append([i, tile_y + 3])

        for i in range(tile_y - 2, tile_y + 3):
            box_list.append([tile_x - 3, i])
            box_list.append([tile_x + 3, i])

        for box in box_list:
            left = box[0]*32
            top = box[1]*32
            box_rects.append(pg.Rect(left, top, 32, 32))

        return box_rects

    def resting(self):
        """
        When the Person is not moving between tiles.
        Checks if the player is centered on a tile.
        """
        self.image = self.image_list[self.index]

    def moving(self):
        """
        Increment index and set self.image for animation.
        """
        self.animation()
        assert(self.rect.x % 32 == 0 or self.rect.y % 32 == 0), \
            'Not centered on tile'

    def animated_resting(self):
        self.animation(500)

    def animation(self):
        """
        Adjust sprite image frame based on timer.
        """
        if self.anim_timer.done():
            if self.index < (len(self.image_list) - 1):
                self.index += 1
            else:
                self.index = 0
            self.anim_timer.reset()

        self.image = self.image_list[self.index]

    def begin_moving(self, direction):
        """
        Transition the player into the 'moving' state.
        """
        self.direction = direction
        self.image_list = self.animation_dict[direction]
        self.state = 'moving'

        if self.rect.x % 32 == 0:
            self.y_vel = self.vector_dict[self.direction][1]
        if self.rect.y % 32 == 0:
            self.x_vel = self.vector_dict[self.direction][0]


    def begin_resting(self):
        """
        Transition the player into the 'resting' state.
        """
        self.state = 'resting'
        self.index = 1
        self.x_vel = self.y_vel = 0

    def begin_auto_moving(self, direction):
        """
        Transition sprite to a automatic moving state.
        """
        self.direction = direction
        self.image_list = self.animation_dict[direction]
        self.state = 'automoving'
        self.x_vel = self.vector_dict[direction][0]
        self.y_vel = self.vector_dict[direction][1]

    def begin_auto_resting(self):
        """
        Transition sprite to an automatic resting state.
        """
        self.state = 'autoresting'
        self.index = 1
        self.x_vel = self.y_vel = 0


    def auto_resting(self):
        """
        Determine when to move a sprite from resting to moving in a random
        direction.
        """
        self.image_list = self.animation_dict[self.direction]
        self.image = self.image_list[self.index]

        if self.move_timer.done():
            direction_list = ['up', 'down', 'left', 'right']
            random.shuffle(direction_list)
            direction = direction_list[0]
            self.begin_auto_moving(direction)
            self.move_timer.reset()

    def battle_resting(self):
        """
        Player stays still during battle state unless he attacks.
        """
        pass

    def enter_attack_state(self, enemy):
        """
        Set values for attack state.
        """
        self.notify(c.SWORD)
        self.attacked_enemy = enemy
        self.x_vel = -5
        self.state = 'attack'


    def attack(self):
        """
        Player does an attack animation.
        """
        fast_forward = -5
        fast_back = 5

        self.rect.x += self.x_vel

        if self.x_vel == fast_forward:
            self.image = self.spritesheet_dict['facing left 1']
            self.image = pg.transform.scale2x(self.image)
            if self.rect.x <= self.origin_pos[0] - 110:
                self.x_vel = fast_back
                self.notify(c.ENEMY_DAMAGED)
        else:
            if self.rect.x >= self.origin_pos[0]:
                self.rect.x = self.origin_pos[0]
                self.x_vel = 0
                self.state = 'battle resting'
                self.image = self.spritesheet_dict['facing left 2']
                self.image = pg.transform.scale2x(self.image)
                self.notify(c.PLAYER_FINISHED_ATTACK)

    def enter_enemy_attack_state(self):
        """
        Set values for enemy attack state.
        """
        self.x_vel = -5
        self.state = 'enemy attack'
        self.origin_pos = self.rect.topleft
        self.move_counter = 0

    def enemy_attack(self):
        """
        Enemy does an attack animation.
        """
        fast_left = -5
        fast_right = 5
        start_x = self.origin_pos[0]

        self.rect.x += self.x_vel

        if self.move_counter == 3:
            self.x_vel = 0
            self.state = 'battle resting'
            self.rect.x = start_x
            self.notify(c.PLAYER_DAMAGED)

        elif self.x_vel == fast_left:
            if self.rect.x <= (start_x - 15):
                self.x_vel = fast_right
        elif self.x_vel == fast_right:
            if self.rect.x >= (start_x + 15):
                self.move_counter += 1
                self.x_vel = fast_left

    def auto_moving(self):
        """
        Animate sprite and check to stop.
        """
        self.animation()

        assert(self.rect.x % 32 == 0 or self.rect.y % 32 == 0), \
            'Not centered on tile'

    def notify(self, event):
        """
        Notify all observers of events.
        """
        for listener in self.observers:
            listener.on_notify(event)

    def calculate_hit(self, armor_list, inventory):
        """
        Calculate hit strength based on attack stats.
        """
        armor_power = 0
        for armor in armor_list:
            armor_power += inventory[armor]['power']
        max_strength = max(1, (self.level * 5) - armor_power)
        min_strength = 0
        return random.randint(min_strength, max_strength)

    def run_away(self):
        """
        Run away from battle state.
        """
        x_vel = 5
        self.rect.x += x_vel
        self.direction = 'right'
        self.small_image_list = self.animation_dict[self.direction]
        self.image_list = []
        for image in self.small_image_list:
            self.image_list.append(pg.transform.scale2x(image))
        self.animation()

    def victory_dance(self):
        """
        Post Victory Dance.
        """
        self.small_image_list = self.animation_dict[self.direction]
        self.image_list = []
        for image in self.small_image_list:
            self.image_list.append(pg.transform.scale2x(image))
        #self.animation(500)
        self.animation()

    def knock_back(self):
        """
        Knock back when hit.
        """
        forward_vel = -2

        self.rect.x += self.x_vel

        if self.name == 'player':
            if self.rect.x >= (self.origin_pos[0] + 10):
                self.x_vel = forward_vel
            elif self.rect.x <= self.origin_pos[0]:
                self.rect.x = self.origin_pos[0]
                self.state = 'battle resting'
                self.x_vel = 0
        else:
            if self.rect.x <= (self.origin_pos[0] - 10):
                self.x_vel = 2
            elif self.rect.x >= self.origin_pos[0]:
                self.rect.x = self.origin_pos[0]
                self.state = 'battle resting'
                self.x_vel = 0

    def fade_death(self):
        """
        Make character become transparent in death.
        """
        self.image = pg.Surface((64, 64)).convert()
        self.image.set_colorkey(c.BLACK)
        self.image.set_alpha(self.alpha)
        self.image.blit(self.death_image, (0, 0))
        self.alpha -= 8
        if self.alpha <= 0:
            self.kill()
            self.notify(c.ENEMY_DEAD)


    def enter_knock_back_state(self):
        """
        Set values for entry to knock back state.
        """
        if self.name == 'player':
            self.x_vel = 4
        else:
            self.x_vel = -4

        self.state = c.KNOCK_BACK
        self.origin_pos = self.rect.topleft


class Player(Person):
    """
    User controlled character.
    """

    def __init__(self, direction, game_data,
                 x=0, y=0, state='resting', index=0):
        super(Player, self).__init__('player', x, y, direction, state, index)
        self.damaged = False
        self.healing = False
        self.damage_alpha = 0
        self.healing_alpha = 0
        self.fade_in = True
        self.game_data = game_data
        self.index = 1
        self.image = self.image_list[self.index]

    @property
    def level(self):
        """
        Make level property equal to player level in game_data.
        """
        return self.game_data['player stats']['Level']


    def create_vector_dict(self):
        """Return a dictionary of x and y velocities set to
        direction keys."""
        self.vector_dict = {'up': (0, -2),
                            'down': (0, 2),
                            'left': (-2, 0),
                            'right': (2, 0)}

    def update(self, keys=None):
        """Updates player behavior"""
        self.damage_animation()
        self.healing_animation()
        self.blockers = self.set_blockers()
        self.keys = keys
        self.check_for_input()
        state_function = self.state_dict[self.state]
        state_function()
        self.location = self.get_tile_location()

    def damage_animation(self):
        """
        Put a red overlay over sprite to indicate damage.
        """
        if self.damaged:
            self.image = copy.copy(self.spritesheet_dict['facing left 2'])
            self.image = pg.transform.scale2x(self.image).convert_alpha()
            damage_image = copy.copy(self.image).convert_alpha()
            damage_image.fill((255, 0, 0, self.damage_alpha),
                              special_flags=pg.BLEND_RGBA_MULT)
            self.image.blit(damage_image, (0, 0))
            if self.fade_in:
                self.damage_alpha += 25
                if self.damage_alpha >= 255:
                    self.fade_in = False
                    self.damage_alpha = 255
            elif not self.fade_in:
                self.damage_alpha -= 25
                if self.damage_alpha <= 0:
                    self.damage_alpha = 0
                    self.damaged = False
                    self.fade_in = True
                    self.image = self.spritesheet_dict['facing left 2']
                    self.image = pg.transform.scale2x(self.image)

    def healing_animation(self):
        """
        Put a green overlay over sprite to indicate healing.
        """
        if self.healing:
            self.image = copy.copy(self.spritesheet_dict['facing left 2'])
            self.image = pg.transform.scale2x(self.image).convert_alpha()
            healing_image = copy.copy(self.image).convert_alpha()
            healing_image.fill((0, 255, 0, self.healing_alpha),
                               special_flags=pg.BLEND_RGBA_MULT)
            self.image.blit(healing_image, (0, 0))
            if self.fade_in:
                self.healing_alpha += 25
                if self.healing_alpha >= 255:
                    self.fade_in = False
                    self.healing_alpha = 255
            elif not self.fade_in:
                self.healing_alpha -= 25
                if self.healing_alpha <= 0:
                    self.healing_alpha = 0
                    self.healing = False
                    self.fade_in = True
                    self.image = self.spritesheet_dict['facing left 2']
                    self.image = pg.transform.scale2x(self.image)

    def check_for_input(self):
        """Checks for player input"""
        if self.state == 'resting':
            if self.keys[pg.K_UP]:
                self.begin_moving('up')
            elif self.keys[pg.K_DOWN]:
                self.begin_moving('down')
            elif self.keys[pg.K_LEFT]:
                self.begin_moving('left')
            elif self.keys[pg.K_RIGHT]:
                self.begin_moving('right')

    def calculate_hit(self, unused_armor_list=None, unused_inventory=None):
        """
        Calculate hit strength based on attack stats.


        """
        weapon = self.game_data['player inventory']['equipped weapon']
        weapon_power = self.game_data['player inventory'][weapon]['power']
        max_strength = weapon_power
        min_strength = max_strength - 7
        return random.randint(min_strength, max_strength)


class Enemy(Person):
    """
    Enemy sprite.
    """
    def __init__(self, sheet_key, x, y,
                 direction='down', state='resting', index=0):
        super(Enemy, self).__init__(sheet_key, x, y, direction, state, index)
        self.level = 1
        self.type = 'enemy'


class Chest(Person):
    """
    Treasure chest that contains items to collect.
    """
    def __init__(self, x, y, identifier):
        super(Chest, self).__init__('treasurechest', x, y)
        self.spritesheet_dict = self.make_image_dict()
        self.image_list = self.make_image_list()
        self.image = self.image_list[self.index]
        self.rect = self.image.get_rect(x=x, y=y)
        self.identifier = identifier

    def make_image_dict(self):
        """
        Make a dictionary for the sprite's images.
        """
        sprite_sheet = setup.gfx()['treasurechest']
        image_dict = {'closed': self.get_image(0, 0, 32, 32, sprite_sheet),
                      'opened': self.get_image(32, 0, 32, 32, sprite_sheet)}

        return image_dict

    def make_image_list(self):
        """
        Make the list of two images for the chest.
        """
        image_list = [self.spritesheet_dict['closed'],
                      self.spritesheet_dict['opened']]

        return image_list

    def update(self, unused_keys=None):
        """Implemented by inheriting classes"""
        self.blockers = self.set_blockers()
        state_function = self.state_dict[self.state]
        state_function()
        self.location = self.get_tile_location()

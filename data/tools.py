"""

Control, state, loaders

"""

__author__ = 'justinarmstrong'

import pygame as pg
from . import constants as c
from . import setup

class Timer(object):
    """
    Is initialized with a number of milliseconds, answers "done" when that
    time has passed; can be reset

    """

    def __init__(self, milliseconds):
        self.milliseconds = milliseconds
        self.start_time = pg.time.get_ticks()

    def done(self, target=None):
        if target is None:
            return (pg.time.get_ticks() - self.start_time) > self.milliseconds
        else:
            return (pg.time.get_ticks() - self.start_time) > target

    def reset(self):
        self.start_time = pg.time.get_ticks()

class Control(object):
    """
    Control class for entire project.  Contains the game loop, and contains
    the event_loop which passes events to States as needed.  Logic for flipping
    states is also found here.
    """
    def __init__(self):

        # stop condition
        self.quit = False

        # clock
        self.clock = pg.time.Clock()

        # 'setup.keys()' keeps a global key state; it's updated
        # with update_keys
        setup.update_keys()

        # (derived from) State
        # .state is the .state_name'ish member of .state_dict
        self.state_dict = {}
        self.state_name = None
        self.state = None

    def setup_states(self, state_dict, start_state):
        """ Set the pool of states and choose one; because of the choosing,
        make sure its music is set

        """

        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

        #self.set_music()

    def update(self):
        """
        Propagate the update tick to the current state; if the current state
        is done, advance to the next

        """

        if self.state.done:
            # turn off this state's 'done' before leaving it, or hanged
            # loop behavior could appear when returning
            self.state.done = False
            self.flip_state()

        self.state.update()

    def flip_state(self):
        """ Choose a new state from the pool; if the state changed,
        maybe the music changes too

        """

        # keep some info of the current state
        current_name = self.state_name

        # update
        self.state_name = self.state.next
        self.state = self.state_dict[self.state_name]

        # store that saved info on the new state
        self.state.previous = current_name

        # initialize the new state
        self.state.startup()
        setup.mixer().play(self.state.name)

    def event_loop(self):
        events = pg.event.get()

        for event in events:
            if event.type == pg.QUIT:
                self.quit = True

            elif event.type == pg.KEYDOWN or event.type == pg.KEYUP:
                setup.update_keys()
                if setup.keys()[pg.K_q]:
                    self.quit = True

            self.state.get_event(event)

    def main(self):
        """Main loop for entire program"""
        while not self.quit:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(c.FPS)

class State(object):
    """Base class for all game states"""
    def __init__(self):
        self.done = False

        self.name = None

        self.next = None

        self.previous = None

        #self.transition_surface = pg.Surface(setup.screen_rect().size)
        #self.transition_surface.fill(c.TRANSITION_COLOR)
        #self.transition_surface.set_alpha(255)

        #self.transition_rect = setup.screen().get_rect()
        #self.transition_alpha = 255

        self.state = None

    def get_event(self, event):
        pass

    def startup(self):
        pass

    def update(self):
        pass

    def make_state_dict(self):
        """
        Make the dicitonary of state methods for the scene.
        """
        state_dict = {c.TRANSITION_IN: self.transition_in,
                      c.TRANSITION_OUT: self.transition_out,
                      c.NORMAL: self.normal_update}

        return state_dict

    def make_sprite(self, key, coords, pos, resize=None):
        """
        Get the image for a character.

        """

        (coordx, coordy) = coords
        (pos_x, pos_y) = pos

        spritesheet = setup.gfx()[key]
        surface = pg.Surface((32, 32))
        surface.set_colorkey(c.BLACK)
        image = get_image(coordx, coordy, 32, 32, spritesheet)
        rect = image.get_rect()
        surface.blit(image, rect)

        if resize is not None:
            surface = pg.transform.scale(surface, (resize, resize))

        rect = surface.get_rect(left=pos_x, top=pos_y)
        sprite = pg.sprite.Sprite()
        sprite.image = surface
        sprite.rect = rect

        return sprite

    def transition_in(self, surface=None):
        """
        Transition into level.
        """

        self.state = 'normal'

        if surface is not None:
            self.draw_level(surface)

        #self.transition_surface.set_alpha(self.transition_alpha)
        #if surface is not None:
        #    self.draw_level(surface)
        #    surface.blit(self.transition_surface, self.transition_rect)
        #self.transition_alpha -= c.TRANSITION_SPEED
        #if self.transition_alpha <= 0:
        #    self.state = 'normal'
        #    self.transition_alpha = 0

    def transition_out(self):
        """
        Transition level to new scene.
        """
        self.done = True

        #transition_image = pg.Surface(self.transition_rect.size)
        #transition_image.fill(c.TRANSITION_COLOR)
        #transition_image.set_alpha(self.transition_alpha)
        #if surface is not None:
        #    self.draw_level(surface)
        #    surface.blit(self.transition_surface, self.transition_rect)
        #self.transition_alpha += c.TRANSITION_SPEED
        #if self.transition_alpha >= 255:
        #    self.done = True

def get_image(pos_x, pos_y, width, height, sprite_sheet):
    """ Extracts image from sprite sheet """

    image = pg.Surface((width, height))

    image.blit(sprite_sheet, (0, 0), (pos_x, pos_y, width, height))
    image.set_colorkey(c.BLACK)

    return image

def get_tile(pos, tileset, dims=(16, 16), scale=1):
    """Gets the surface and rect for a tile"""
    (pos_x, pos_y) = pos
    (width, height) = dims
    surface = get_image(pos_x, pos_y, width, height, tileset)
    surface = pg.transform.scale(surface, (int(width*scale), int(height*scale)))
    rect = surface.get_rect()

    tile_dict = {'surface': surface,
                 'rect': rect}

    return tile_dict

def notify_observers(self, event):
    """
    Notify all observers of events.
    """
    for each_observer in self.observers:
        each_observer.on_notify(event)

def create_game_data_dict():
    """Create a dictionary of persistant values the player
    carries between states"""

    player_items = {'GOLD': dict([('quantity', 10000),
                                  ('value', 0)]),
                    'Healing Potion': dict([('quantity', 2),
                                            ('value', 15)]),
                    'Ether Potion': dict([('quantity', 1),
                                          ('value', 15)]),
                    'Rapier': dict([('quantity', 1),
                                    ('value', 50),
                                    ('power', 9)]),
                    'equipped weapon': 'Rapier',
                    'equipped armor': []}

    player_health = {'current': 70,
                     'maximum': 70}

    player_magic = {'current': 7000,
                    'maximum': 7000}

    player_stats = {'health': player_health,
                    'Level': 1,
                    'experience to next level': 30,
                    'magic': player_magic,
                    'attack points': 10,
                    'Defense Points': 10}


    data_dict = {'last location': None,
                 'last state': None,
                 'last direction': 'down',
                 'king item': 'GOLD',
                 'old man item': {'ELIXIR': dict([('value', 1000),
                                                  ('quantity', 1)])},
                 'player inventory': player_items,
                 'player stats': player_stats,
                 'battle counter': 50,
                 'treasure1': True,
                 'treasure2': True,
                 'treasure3': True,
                 'treasure4': True,
                 'treasure5': True,
                 'start of game': True,
                 'talked to king': False,
                 'brother quest complete': False,
                 'talked to sick brother': False,
                 'has brother elixir': False,
                 'elixir received': False,
                 'old man gift': '',
                 'battle type': '',
                 'crown quest': False,
                 'delivered crown': False,
                 'brother item': 'ELIXIR'}

    setup.register_game_data(data_dict)

def empty_background():
    """
    Creates a generic surface to blit on and use as a "dark color" background

    """

    background = pg.sprite.Sprite()
    surface = pg.Surface(c.SCREEN_SIZE).convert()
    surface.fill(c.BLACK_BLUE)
    background.image = surface
    background.rect = background.image.get_rect()

    return background

class FadeSurface(pg.Surface):
    """
    A surface that has a countdown linked to its alpha value;
    once the countdown is over, the surface is done

    """

    def __init__(self, size):
        super(FadeSurface, self).__init__(size)
        self.alpha = 255
        self.set_alpha(self.alpha)
        self.set_colorkey(c.BLACK)
        self.convert()

    def update_alpha(self, amount):
        self.alpha -= amount
        self.set_alpha(self.alpha)

    def faded(self):
        return self.alpha < 0

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
    def __init__(self, caption):
        # drawable
        self.screen = pg.display.get_surface()
        self.caption = caption
        # stop condition
        self.done = False
        # clock
        self.clock = pg.time.Clock()
        self.show_fps = False
        # all keys' pressed-or-not-pressed state
        self.keys = pg.key.get_pressed()
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
        self.set_music()

    def update(self):
        """ Update self.state... maybe better in State itself?

        """

        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(self.screen, self.keys)

    def flip_state(self):
        """ Choose a new state from the pool; if the state changed,
        maybe the music changes too

        """

        previous, self.state_name = self.state_name, self.state.next
        previous_music = self.state.music_title
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.previous = previous
        self.state.previous_music = previous_music
        self.state.startup(persist)
        self.set_music()

    def set_music(self):
        """
        Set music for the new state.
        """
        if self.state.music_title == self.state.previous_music:
            pass
        elif self.state.music:
            pg.mixer.music.load(self.state.music)
            pg.mixer.music.set_volume(self.state.volume)
            pg.mixer.music.play(-1)

    def event_loop(self):
        events = pg.event.get()

        for event in events:
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
                self.toggle_show_fps(event.key)
                self.state.get_event(event)
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
                self.state.get_event(event)

    def toggle_show_fps(self, key):
        if key == pg.K_F5:
            self.show_fps = not self.show_fps
            if not self.show_fps:
                pg.display.set_caption(self.caption)

    def main(self):
        """Main loop for entire program"""
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(c.FPS)
            if self.show_fps:
                fps = self.clock.get_fps()
                with_fps = "{} - {:.2f} FPS".format(self.caption, fps)
                pg.display.set_caption(with_fps)


class State(object):
    """Base class for all game states"""
    def __init__(self):
        self.start_time = 0.0
        self.done = False
        self.quit = False
        self.next = None
        self.previous = None
        self.game_data = {}
        self.music = None
        self.music_title = None
        self.previous_music = None

        self.transition_surface = pg.Surface(setup.screen_rect().size)
        self.transition_surface.fill(c.TRANSITION_COLOR)
        self.transition_surface.set_alpha(255)

        self.transition_rect = setup.screen().get_rect()
        self.transition_alpha = 255

    def get_event(self, event):
        pass

    def startup(self, game_data):
        self.game_data = game_data

    def cleanup(self):
        self.done = False
        return self.game_data

    def update(self, surface, keys):
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
        image = self.get_image(coordx, coordy, 32, 32, spritesheet)
        rect = image.get_rect()
        surface.blit(image, rect)

        if resize is not None:
            surface = pg.transform.scale(surface, (resize, resize))

        rect = surface.get_rect(left=pos_x, top=pos_y)
        sprite = pg.sprite.Sprite()
        sprite.image = surface
        sprite.rect = rect

        return sprite

    def transition_in(self, surface=None, unused_keys=None):
        """
        Transition into level.
        """
        self.transition_surface.set_alpha(self.transition_alpha)
        if surface is not None:
            self.draw_level(surface)
            surface.blit(self.transition_surface, self.transition_rect)
        self.transition_alpha -= c.TRANSITION_SPEED
        if self.transition_alpha <= 0:
            self.state = 'normal'
            self.transition_alpha = 0

    def transition_out(self, surface=None, unused_keys=None):
        """
        Transition level to new scene.
        """
        transition_image = pg.Surface(self.transition_rect.size)
        transition_image.fill(c.TRANSITION_COLOR)
        transition_image.set_alpha(self.transition_alpha)
        if surface is not None:
            self.draw_level(surface)
            surface.blit(self.transition_surface, self.transition_rect)
        self.transition_alpha += c.TRANSITION_SPEED
        if self.transition_alpha >= 255:
            self.done = True

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

    player_items = {'GOLD': dict([('quantity', 100),
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

    player_magic = {'current': 70,
                    'maximum': 70}

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

    return data_dict

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

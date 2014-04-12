"""This is overworld state.  Most of its functionality is inherited from
the level_state.py module.  Most of the level data is contained in
the tilemap.txt files in this state's directory.
"""

from .. import level_state
from ... import constants as c
from ... import setup

class Overworld(level_state.LevelState):
    def __init__(self):
        super(Overworld, self).__init__()
        self.name = c.OVERWORLD
        self.tmx_map = setup.TMX['overworld']




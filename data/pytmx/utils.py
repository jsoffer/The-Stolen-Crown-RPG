from itertools import tee, islice, product
from collections import defaultdict

from pygame import Rect

from .constants import (GID_TRANS_FLIPX, GID_TRANS_FLIPY,
                        TRANS_FLIPX, TRANS_FLIPY,
                        GID_TRANS_ROT, TRANS_ROT)

def read_points(text):
    return [tuple([int(j) for j in i.split(',')]) for i in text.split()]

def parse_properties(node):
    """
    parse a node and return a dict that represents a tiled "property"
    """

    # the "properties" from tiled's tmx have an annoying quality that "name"
    # and "value" is included. here we mangle it to get that junk out.

    properties = {}

    for child in node.findall('properties'):
        for subnode in child.findall('property'):
            properties[subnode.get('name')] = subnode.get('value')

    return properties


def decode_gid(raw_gid):
    # gids are encoded with extra information
    # as of 0.7.0 it determines if the tile should be flipped when rendered
    # as of 0.8.0 bit 30 determines if GID is rotated

    flags = 0
    if raw_gid & GID_TRANS_FLIPX == GID_TRANS_FLIPX:
        flags += TRANS_FLIPX

    if raw_gid & GID_TRANS_FLIPY == GID_TRANS_FLIPY:
        flags += TRANS_FLIPY

    if raw_gid & GID_TRANS_ROT == GID_TRANS_ROT:
        flags += TRANS_ROT

    gid = raw_gid & ~(GID_TRANS_FLIPX | GID_TRANS_FLIPY | GID_TRANS_ROT)

    return gid, flags


def handle_bool(text):
    """
    Somewhat sketchy way to convert strings to bool objects by abusing the
    exception system

    """

    # properly convert strings to a bool
    try:
        return bool(int(text))
    except ValueError:
        pass

    text = str(text).lower()

    if text == "true":
        return True

    if text == "yes":
        return True

    if text == "false":
        return False

    if text == "no":
        return False

    raise ValueError("handle_bool failed to convert %s to bool" % (text))

# used to change the unicode string returned from xml to proper python
# variable types.
TYPES = defaultdict(lambda: str)
TYPES.update({
    "version": float,
    "orientation": str,
    "width": int,
    "height": int,
    "tilewidth": int,
    "tileheight": int,
    "firstgid": int,
    "source": str,
    "name": str,
    "spacing": int,
    "margin": int,
    "trans": str,
    "id": int,
    "opacity": float,
    "visible": handle_bool,
    "encoding": str,
    "compression": str,
    "gid": int,
    "type": str,
    "x": int,
    "y": int,
    "value": str,
})


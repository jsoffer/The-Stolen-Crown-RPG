"""
This is a test of using the pytmx library with Tiled.
"""
import pygame as pg

from . import pytmx


class Renderer(object):
    """
    This object renders tile maps from Tiled

    'filename' is a TMX map specification file
    'tilemap' is a collection of tiles, all of the same size
    'tilemap.width' and 'tilemap.height' are the number of tiles on the map

    """

    def __init__(self, filename):
        tilemap = pytmx.load_pygame(filename, pixelalpha=True)
        self.size = (
            tilemap.width * tilemap.tilewidth,
            tilemap.height * tilemap.tileheight)
        print(filename, tilemap.width, tilemap.height, tilemap.tilewidth,
              tilemap.tileheight)
        self.tmx_data = tilemap

    def render(self, surface):

        tile_width = self.tmx_data.tilewidth
        tile_height = self.tmx_data.tileheight
        get_tile = self.tmx_data.get_tile_image_by_gid

        if self.tmx_data.background_color:
            surface.fill(self.tmx_data.background_color)

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledLayer):
                for tile_x, tile_y, gid in layer:
                    tile = get_tile(gid)
                    if tile:
                        surface.blit(
                            tile, (tile_x * tile_width, tile_y * tile_height))

            elif isinstance(layer, pytmx.TiledObjectGroup):
                pass

            elif isinstance(layer, pytmx.TiledImageLayer):
                image = get_tile(layer.gid)
                if image:
                    surface.blit(image, (0, 0))

    def make_2x_map(self):
        temp_surface = pg.Surface(self.size)
        self.render(temp_surface)
        temp_surface = pg.transform.scale2x(temp_surface)
        return temp_surface


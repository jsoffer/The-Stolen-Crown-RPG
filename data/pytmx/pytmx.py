from itertools import chain, product
from xml.etree import ElementTree

from .utils import decode_gid, parse_properties, TYPES


__all__ = [
    'TiledMap', 'TiledTileset', 'TiledLayer', 'TiledObject',
    'TiledObjectGroup', 'TiledImageLayer']

class TiledElement(object):
    def set_properties(self, node):
        """
        read the xml attributes and tiled "properties" from a xml node and fill
        in the values into the object's dictionary.  Names will be checked to
        make sure that they do not conflict with reserved names.
        """

        # set the attributes reserved for tiled
        for key, value in node.items():
            setattr(self, key, TYPES[str(key)](value))

        # set the attributes that are derived from tiled 'properties'
        for key, value in parse_properties(node).items():
            if key in self.reserved:
                msg = "{0} \"{1}\" has a property called \"{2}\""
                print(msg.format(self.__class__.__name__, self.name, key,
                                 self.__class__.__name__))
                msg = ("This name is reserved for {0} objects" +
                       " and cannot be used.")
                print(msg.format(self.__class__.__name__))
                print("Please change the name in Tiled and try again.")
                raise ValueError
            setattr(self, key, TYPES[str(key)](value))


class TiledMap(TiledElement):
    """
    Contains the tile layers, tile images, object groups, and objects from a
    Tiled TMX map.
    """

    reserved = (
        "visible version orientation width height tilewidth" +
        " tileheight properties tileset layer objectgroup").split()

    def __init__(self, filename=None):
        from collections import defaultdict

        TiledElement.__init__(self)
        self.tilesets = []  # list of TiledTileset objects
        self.tilelayers = []  # list of TiledLayer objects
        self.imagelayers = []  # list of TiledImageLayer objects
        self.objectgroups = []  # list of TiledObjectGroup objects
        self.all_layers = []  # list of all layers in proper order
        self.tile_properties = {}  # dict of tiles that have metadata
        self.filename = filename

        self.layernames = {}

        # only used tiles are actually loaded, so there will be a difference
        # between the GIDs in the Tile map data (tmx) and the data in this
        # class and the layers.  This dictionary keeps track of that difference.
        self.gidmap = defaultdict(list)

        # should be filled in by a loader function
        self.images = []

        # defaults from the TMX specification
        self.version = 0.0
        self.orientation = None
        self.width = 0       # width of map in tiles
        self.height = 0      # height of map in tiles
        self.tilewidth = 0   # width of a tile in pixels
        self.tileheight = 0  # height of a tile in pixels
        self.background_color = None

        self.imagemap = {}  # mapping of gid and trans flags to real gids
        self.maxgid = 1

        if filename:
            self.load()

    def __repr__(self):
        return "<{0}: \"{1}\">".format(self.__class__.__name__, self.filename)

    def get_tile_image_by_gid(self, gid):
        try:
            assert gid >= 0
            return self.images[gid]
        except (IndexError, ValueError, AssertionError):
            msg = "Invalid GID specified: {}"
            print(msg.format(gid))
            raise ValueError
        except TypeError:
            msg = "GID must be specified as integer: {}"
            print(msg.format(gid))
            raise TypeError

    def get_objects(self):
        """
        Return iterator of all the objects associated with this map
        """

        return chain(*(i for i in self.objectgroups))

    def get_layer_data(self, layer):
        """
        Return the data for a layer.

        Data is an array of arrays.

        >>> pos = data[y][x]
        """

        try:
            return self.tilelayers[layer].data
        except IndexError:
            msg = "Layer {0} does not exist."
            raise ValueError(msg.format(layer))

    def get_tile_properties_by_gid(self, gid):
        try:
            return self.tile_properties[gid]
        except KeyError:
            return None

    def set_tile_properties(self, gid, properties):
        """
        set the properties of a tile by GID.
        must use a standard python dict as 'properties'

        """

        try:
            self.tile_properties[gid] = properties
        except KeyError:
            msg = "GID #{0} does not exist."
            raise ValueError(msg.format(gid))

    def register_gid(self, real_gid, flags=0):
        """
        used to manage the mapping of GID between the tmx data and the internal
        data.

        number returned is gid used internally
        """

        if real_gid:
            try:
                return self.imagemap[(real_gid, flags)][0]
            except KeyError:
                # this tile has not been encountered before, or it has been
                # transformed in some way.  make a new GID for it.
                gid = self.maxgid
                self.maxgid += 1
                self.imagemap[(real_gid, flags)] = (gid, flags)
                self.gidmap[real_gid].append((gid, flags))
                return gid
        else:
            return 0

    def map_gid(self, real_gid):
        """
        used to lookup a GID read from a TMX file's data
        """

        try:
            return self.gidmap[int(real_gid)]
        except KeyError:
            return None
        except TypeError:
            msg = "GIDs must be an integer"
            raise TypeError(msg)

    def load(self):
        """
        parse a map node from a tiled tmx file
        """
        etree = ElementTree.parse(self.filename).getroot()
        self.set_properties(etree)

        # initialize the gid mapping
        self.imagemap[(0, 0)] = 0

        self.background_color = etree.get(
            'backgroundcolor', self.background_color)

        # *** do not change this load order! ***
        # *** gid mapping errors will occur if changed ***

        for node in etree.findall('layer'):
            self.add_tile_layer(TiledLayer(self, node))

        for node in etree.findall('imagelayer'):
            self.add_image_layer(TiledImageLayer(self, node))

        for node in etree.findall('objectgroup'):
            self.objectgroups.append(TiledObjectGroup(self, node))

        for node in etree.findall('tileset'):
            self.tilesets.append(TiledTileset(self, node))

        # "tile objects", objects with a GID, have need to have their
        # attributes set after the tileset is loaded, so this step
        # must be performed last

        for obj in self.objects:
            properties = self.get_tile_properties_by_gid(obj.gid)
            if properties:
                obj.__dict__.update(properties)

    def add_tile_layer(self, layer):
        """
        Add a TiledLayer layer object to the map.
        """

        if not isinstance(layer, TiledLayer):
            msg = "Layer must be an TiledLayer object.  Got {0} instead."
            raise ValueError(msg.format(type(layer)))

        self.tilelayers.append(layer)
        self.all_layers.append(layer)
        self.layernames[layer.name] = layer

    def add_image_layer(self, layer):
        """
        Add a TiledImageLayer layer object to the map.
        """

        if not isinstance(layer, TiledImageLayer):
            msg = "Layer must be an TiledImageLayer object.  Got {0} instead."
            raise ValueError(msg.format(type(layer)))

        self.imagelayers.append(layer)
        self.all_layers.append(layer)
        self.layernames[layer.name] = layer

    @property
    def objects(self):
        """
        Return iterator of all the objects associated with this map
        """
        return chain(*self.objectgroups)

    @property
    def visible_layers(self):
        """
        Returns a generator of [Image/Tile]Layer objects that are set 'visible'.

        Layers have their visibility set in Tiled.
        """
        return (l for l in self.all_layers if l.visible)


class TiledTileset(TiledElement):
    reserved = ("visible firstgid source name tilewidth tileheight" +
                " spacing margin image tile properties").split()

    def __init__(self, parent, node):
        TiledElement.__init__(self)
        self.parent = parent

        # defaults from the specification
        self.firstgid = 0
        self.source = None
        self.name = None
        self.tilewidth = 0
        self.tileheight = 0
        self.spacing = 0
        self.margin = 0
        self.tiles = {}
        self.trans = None
        self.width = 0
        self.height = 0

        self.parse(node)

    def __repr__(self):
        return "<{0}: \"{1}\">".format(self.__class__.__name__, self.name)

    def parse(self, node):
        """
        parse a tileset element and return a tileset object and properties for
        tiles as a dict

        a bit of mangling is done here so that tilesets that have external
        TSX files appear the same as those that don't
        """
        import os

        # if true, then node references an external tileset
        source = node.get('source', False)
        if source:
            if source[-4:].lower() == ".tsx":

                # external tilesets don't save this, store it for later
                self.firstgid = int(node.get('firstgid'))

                # we need to mangle the path - tiled stores relative paths
                dirname = os.path.dirname(self.parent.filename)
                path = os.path.abspath(os.path.join(dirname, source))
                try:
                    node = ElementTree.parse(path).getroot()
                except IOError:
                    msg = "Cannot load external tileset: {0}"
                    raise Exception(msg.format(path))

            else:
                msg = "Found external tileset, but cannot handle type: {0}"
                raise Exception(msg.format(self.source))

        self.set_properties(node)

        # since tile objects [probably] don't have a lot of metadata,
        # we store it separately in the parent (a TiledMap instance)
        for child in node.getiterator('tile'):
            real_gid = int(child.get("id"))
            properties = parse_properties(child)
            properties['width'] = self.tilewidth
            properties['height'] = self.tileheight
            for gid, _ in self.parent.map_gid(real_gid + self.firstgid):
                self.parent.set_tile_properties(gid, properties)

        image_node = node.find('image')
        self.source = image_node.get('source')
        self.trans = image_node.get("trans", None)


class TiledLayer(TiledElement):
    reserved = "visible name x y width height opacity properties data".split()

    def __init__(self, parent, node):
        TiledElement.__init__(self)
        self.parent = parent
        self.data = []

        # defaults from the specification
        self.name = None
        self.opacity = 1.0
        self.visible = True

        self.parse(node)

    def __iter__(self):
        return self.iter_tiles()

    def iter_tiles(self):
        for tile_y, tile_x in product(range(self.height), range(self.width)):
            yield tile_x, tile_y, self.data[tile_y][tile_x]

    def __repr__(self):
        return "<{0}: \"{1}\">".format(self.__class__.__name__, self.name)

    def parse(self, node):
        """
        parse a layer element
        """

        from struct import unpack
        import array

        self.set_properties(node)

        data = None
        next_gid = None

        data_node = node.find('data')

        encoding = data_node.get("encoding", None)
        if encoding == "base64":
            from base64 import decodestring

            data = decodestring(data_node.text.strip().encode())

        elif encoding == "csv":

            next_gid = (int(k) for k in
                        "".join(
                            line.strip() for line in data_node.text.strip()
                        ).split(","))

        elif encoding:
            msg = "TMX encoding type: {0} is not supported."
            raise Exception(msg.format(encoding))

        compression = data_node.get("compression", None)
        if compression == "gzip":
            from io import StringIO
            import gzip

            file_handle = gzip.GzipFile(fileobj=StringIO(data))
            data = file_handle.read()
            file_handle.close()

        elif compression == "zlib":
            import zlib

            data = zlib.decompress(data)

        elif compression:
            msg = "TMX compression type: {0} is not supported."
            raise Exception(msg.format(compression))

        # if data is None, then it was not decoded or decompressed, so
        # we assume here that it is going to be a bunch of tile elements
        if encoding == next_gid is None:
            def get_children(parent):
                for child in parent.findall('tile'):
                    yield int(child.get('gid'))

            next_gid = get_children(data_node)

        elif data:
            # data is a list of gids. cast as 32-bit ints to format properly
            # create iterator to efficiently parse data
            next_gid = (
                unpack("<L", data[k:k+4])[0] for k in range(0, len(data), 4))

        # using bytes here limits the layer to 256 unique tiles
        # may be a limitation for very detailed maps, but most maps are not
        # so detailed.

        self.data += [array.array('H') for k in range(self.height)]

        for (tile_y, _) in product(range(self.height), range(self.width)):
            self.data[tile_y].append(
                self.parent.register_gid(*decode_gid(next(next_gid))))

class TiledObjectGroup(TiledElement, list):
    """
    Stores TiledObjects.  Supports any operation of a normal list.
    """
    reserved = ("visible name color x y width height" +
                " opacity object properties").split()

    def __init__(self, parent, node):
        super(TiledObjectGroup, self).__init__(self)

        self.parent = parent

        # defaults from the specification
        self.name = None
        self.color = None
        self.opacity = 1
        self.visible = 1
        self.parse(node)

    def __repr__(self):
        return "<{0}: \"{1}\">".format(self.__class__.__name__, self.name)

    def parse(self, node):
        """
        parse a objectgroup element and return a object group
        """

        self.set_properties(node)

        for child in node.findall('object'):
            obj = TiledObject(self.parent, child)
            self.append(obj)

class TiledObject(TiledElement):
    reserved = ("visible name type x y width height gid properties" +
                " polygon polyline image").split()

    def __init__(self, parent, node):
        TiledElement.__init__(self)
        self.parent = parent

        # defaults from the specification
        self.name = None
        self.type = None
        self.width = 0
        self.height = 0
        self.rotation = 0
        self.gid = 0
        self.visible = 1

        self.parse(node)

    def __repr__(self):
        return "<{0}: \"{1}\">".format(self.__class__.__name__, self.name)

    def parse(self, node):
        self.set_properties(node)

        # correctly handle "tile objects" (object with gid set)
        if self.gid:
            self.gid = self.parent.register_gid(self.gid)

class TiledImageLayer(TiledElement):
    reserved = "visible source name width height opacity visible".split()

    def __init__(self, parent, node):
        TiledElement.__init__(self)
        self.parent = parent
        self.source = None
        self.trans = None

        # unify the structure of layers
        self.gid = 0

        # defaults from the specification
        self.name = None
        self.opacity = 1
        self.visible = 1

        self.parse(node)

    def parse(self, node):
        self.set_properties(node)

        self.name = node.get('name', None)
        self.opacity = node.get('opacity', self.opacity)
        self.visible = node.get('visible', self.visible)

        image_node = node.find('image')
        self.source = image_node.get('source')
        self.trans = image_node.get('trans', None)

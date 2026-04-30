import overpy

from common.cache import Cacheable
from common.environment import StaticEntity, bounding_box, island, waters
from common.serialization import serialize_list, deserialize_list
from common import logging
from common.types import BoundingBox, Coords, CoordsList
from common.units import DD, toDD

Refs = dict[int, str]
Ways = dict[int, list[overpy.Node]]

log = logging.getLogger(__name__)


def vertices(entity: list[overpy.Node]) -> CoordsList:
    """Convert overpy.Node to vertices"""
    return [DD(float(node.lat), float(node.lon)) for node in entity]


class OSMSupplier(Cacheable):
    """OpenStreetMap map data supplier."""
    api: overpy.Overpass
    position: Coords
    query_bounding_box: BoundingBox
    bounding_box: BoundingBox
    viewing_dist: float

    def __init__(self, position: Coords, viewing_dist: float):
        self.api = overpy.Overpass(
            max_retry_count=10,
            retry_timeout=10.0
        )
        self.set_query_bounding_box(position, viewing_dist)

    def set_query_bounding_box(self, position: Coords, delta: float):
        self.cleanup()
        self.position = position
        self.viewing_dist = delta
        self.query_bounding_box = (position[0] - delta, position[1] - delta,
                                   position[0] + delta, position[1] + delta)

    @property
    def query(self) -> str:
        """So far lakes and large rivers supported."""
        bb = self.query_bounding_box
        bb_dd = (*toDD(bb[0], bb[1]), *toDD(bb[2], bb[3]))
        return f'''[out: json][timeout: 25];
               (
               way["natural" = "water"]{bb_dd};
               way["waterway" = "river"]{bb_dd};
               relation["natural" = "water"]{bb_dd};
               );
               out; >;out skel qt;'''

    def cleanup(self):
        '''Cleanup fetched and parsed data'''
        self.data = None
        self.statics = None

    def fetch(self):
        """Fetch data from OpenStreetMap server."""
        log.debug('Fetching data from OSM server')
        query = self.query
        log.debug(f'query={query}')
        self.data = self.api.query(query)
        log.info('Received data from OSM server')

    def get_relations(self) -> list:
        return [relation.members for relation in self.data.relations]

    def get_refs(self) -> Refs:
        return {j.ref: j.role for i in self.get_relations() for j in i}

    def get_ways(self) -> Ways:
        """
        Returns:
            dict with a list of nodes and a corresponding wayID
        """
        return {way.id: way.nodes for way in self.data.ways}

    def get_terrain(self, refs: Refs, ways: Ways, io: str) -> list:
        return [ways[ref] for ref in refs if refs[ref] == io]

    def get_ways_with_no_relation(self, refs: Refs, ways: Ways) -> list:
        return [ways[way] for way in ways if way not in refs.keys()]

    def parse(self):
        if self.data is None:
            self.fetch()

        refs = self.get_refs()
        ways = self.get_ways()
        islands_list = self.get_terrain(refs, ways, 'inner')
        waters_list = (self.get_terrain(refs, ways, 'outer') +
                       self.get_ways_with_no_relation(refs, ways))

        self.statics = []
        self.statics = [island(vertices(i)) for i in islands_list]
        self.statics.extend(waters([vertices(w) for w in waters_list]))
        self.bounding_box = bounding_box(self.statics)

    def get_entities(self) -> list[StaticEntity]:
        if self.statics is None:
            if not self.cache_load():
                self.parse()
                self.cache_save()

        return self.statics

    def cache_params(self):
        try:
            xmin, ymin, xmax, ymax = self.bounding_box
        except AttributeError:
            return  # skip cache_params for loading cache
        yield xmin
        yield ymin
        yield xmax
        yield ymax

    def cache_is_usable(self, *params) -> bool:
        try:
            xmin, ymin, xmax, ymax = [float(x) for x in params[1:5]]
        except ValueError:
            return False
        x, y = self.position
        return xmin <= x <= xmax and ymin <= y <= ymax

    def serialize(self) -> dict:
        return {
            'position': self.position,
            'viewing_dist': self.viewing_dist,
            'query_bounding_box': self.query_bounding_box,
            'statics': serialize_list(self.statics)
        }

    def deserialize(self, dictionary: dict):
        super().deserialize(dictionary)
        self.position = tuple(self.position)
        self.query_bounding_box = tuple(self.query_bounding_box)
        self.statics = deserialize_list(self.statics, StaticEntity)

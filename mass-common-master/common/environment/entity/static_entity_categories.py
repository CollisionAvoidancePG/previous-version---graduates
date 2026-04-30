from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

from common.types import CoordsList
from common.units import m

from . import StaticEntity


def island(vertices: CoordsList) -> StaticEntity:
    entity = StaticEntity(vertices, safe_zone_size=3*m)
    entity.category = 'island'
    entity.model_color = 'lightgreen'
    return entity


def land(vertices: CoordsList) -> StaticEntity:
    entity = StaticEntity(vertices, safe_zone_size=3*m)
    entity.category = 'land'
    entity.model_color = 'lightgreen'
    return entity


def waters(waters: list[CoordsList]) -> list[StaticEntity]:
    """Convert waters into land category entities"""
    # skip unary_union if there is only one water entity
    if len(waters) > 1:
        water = unary_union([Polygon(vertices) for vertices in waters])
    else:
        water = Polygon(waters[0])

    x1, y1, x2, y2 = water.bounds
    bb = Polygon([(x1, y1), (x1, y2), (x2, y2), (x2, y1)])
    result = bb.symmetric_difference(water)
    if isinstance(result, MultiPolygon):
        return [land(polygon) for polygon in result.geoms]
    else:
        raise NotImplementedError(
            f"Result of symmetric difference on waters is {type(result)}")


def detected(vertices: CoordsList) -> StaticEntity:
    entity = StaticEntity(vertices, safe_zone_size=0)
    entity.category = 'detected'
    entity.model_color = 'green'
    entity.hover_info = True
    return entity


def virtual(vertices: CoordsList) -> StaticEntity:
    entity = StaticEntity(vertices, safe_zone_size=0)
    entity.category = 'virtual'
    entity.model_color = None
    entity.hover_info = True
    return entity

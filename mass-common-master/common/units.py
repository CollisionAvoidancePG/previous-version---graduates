"""Unit conversions module"""
import pyproj
import numpy as np

from common.types import Coords


#
# angle
#
rad = 1
deg = np.pi / 180


def toCD(course_deg: float) -> str:
    """Convert `course` in degrees to Cardinal Direction"""
    course = course_deg

    if (course > 22.5 * 15 or course <= 22.5 * 1):
        return "N"
    elif (22.5 * 1 < course <= 22.5 * 3):
        return "NE"
    elif (22.5 * 3 < course <= 22.5 * 5):
        return "E"
    elif (22.5 * 5 < course <= 22.5 * 7):
        return "SE"
    elif (22.5 * 7 < course <= 22.5 * 9):
        return "S"
    elif (22.5 * 9 < course <= 22.5 * 11):
        return "SW"
    elif (22.5 * 11 < course <= 22.5 * 13):
        return "W"
    elif (22.5 * 13 < course <= 22.5 * 15):
        return "NW"


#
# length
#
mm = 0.001
cm = 0.01
dm = 0.1
m = 1
km = 1000
mi = 1609.344
NM = 1852

_wgs84 = pyproj.CRS('EPSG:4326')
_wgs84_proj = pyproj.CRS('EPSG:3857')

_wgs84_to_wgs84_proj = pyproj.Transformer.from_crs(_wgs84, _wgs84_proj, always_xy=False).transform
_wgs84_proj_to_wgs84 = pyproj.Transformer.from_crs(_wgs84_proj, _wgs84, always_xy=False).transform


def DD(latitude: float, longitude: float) -> Coords:  # noqa: N802,E501
    """Latitude and longitude projection to XY"""
    return _wgs84_to_wgs84_proj(latitude, longitude)


def toDD(x: float, y: float) -> Coords:  # noqa: N802
    """XY to latitude and longitude"""
    return _wgs84_proj_to_wgs84(x, y)


#
# velocity
#
mps = 1
kn = 1.94384449
kmph = 3.6

#
# time
#
s = 1
min = 60
h = 3600

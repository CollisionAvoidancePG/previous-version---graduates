from common.environment import Environment, boat
from common.units import deg, mps, DD
from common.viewer import Viewer

from osm import OSMSupplier

pos = DD(54.31748, 18.58226)  # Świętokrzyska
# pos = DD(54.41970, 18.62360)  # Jelitkowo - Morze
# pos = DD(54.31414, 18.50425)  # Otomin

statics = OSMSupplier(pos, 150).get_entities()

env = Environment(
    statics=statics,
    dynamics=[
        boat(DD(54.31690, 18.57856), 4 * mps, 97 * deg),
        boat(DD(54.31785, 18.57819), 1.66 * mps, 334 * deg)
    ]
)

Viewer(title="Map", draw=[env])

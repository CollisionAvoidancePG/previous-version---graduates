from shapely.geometry import Polygon

from common.serialization import Serializable
from common.types import CoordsList

from .args import parser

args, _ = parser.parse_known_args()


class Entity(Serializable):
    """Base environment entity"""
    category: str = None
    safe_zone: Polygon
    model: Polygon
    safe_zone_color: str = 'red'
    model_color: str = 'black'
    hover_info: bool = False

    def __init__(self, safe_zone: CoordsList, model: CoordsList = None):
        self.safe_zone = Polygon(safe_zone)
        self.model = None if args.models_disabled else Polygon(model)

    def _draw_polygon(self, go, fig, polygon, color, opacity=1.0):
        x, y = polygon.exterior.xy
        fig.add_traces(go.Scatter(
            x=list(x),
            y=list(y),
            showlegend=False,
            fill="toself",
            fillcolor=color,
            opacity=opacity,
            mode='none',
            hoverinfo='skip' if self.hover_info is None else 'text',
            name='',
            text=str(self)
        ))

    def draw(self, go, fig):
        self._draw_polygon(go, fig, self.safe_zone, self.safe_zone_color, opacity=0.2)
        if not args.models_disabled and self.model_color is not None:
            self._draw_polygon(go, fig, self.model, self.model_color)

    def serialize(self) -> dict:
        return {
            "category": self.category,
            "safe_zone": [xy for xy in self.safe_zone.exterior.coords],
            "model": [xy for xy in self.model.exterior.coords],
        }

    def deserialize(self, dictionary: dict):
        super().deserialize(dictionary)
        self.safe_zone = Polygon(self.safe_zone)
        self.model = Polygon(self.model)

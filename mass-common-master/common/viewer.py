from typing import Union
import plotly.graph_objects as go


class Viewer:
    def __init__(self, *, title: str = "", draw: Union[list, tuple], annotation: str = None):
        layout = {
            'title': title,
            'xaxis': {
                'showgrid': False,
            },
            'yaxis': {
                'showgrid': False,
            },
            'dragmode': 'pan'
        }
        self.fig = go.Figure(layout=layout)
        self.max_iterables = 0
        self.iterables = []

        if annotation is not None:
            self.fig.add_annotation(text=annotation, xref="paper", yref="paper",
                                    x=0.01, y=0.99, showarrow=False, align="left")

        if isinstance(draw, list):
            self.__list_variant(draw)
        elif isinstance(draw, tuple):
            self.__tuple_variant(draw)

        self.show()

    def show(self):
        self.fig.show(config={'scrollZoom': True})

    def __list_variant(self, draw):
        self.fig.layout.yaxis.scaleanchor = 'x'
        for d in draw:
            if isinstance(d, list):  # list of drawable objects (slider iterable)
                self.iterables.append(d)
                self.max_iterables = max(self.max_iterables, len(d))
            else:  # drawable objects
                d.draw(go, self.fig)

        self.__prepare_slider()

    def __tuple_variant(self, draw):
        for k, v in draw[0].items():
            self.fig.add_trace(go.Scatter(
                x=list(range(len(v))),
                y=v,
                name=k,
                customdata=draw[1],
                hovertemplate=(
                    "%{y}<br>"
                    "<b>Generation %{x}</b><br>"
                    "<i>last operation: %{customdata}</i>"
                ),
            ))

    def __prepare_slider(self):
        if (self.max_iterables == 0):
            return

        # this table contains visibility for all drawn items used to determine what should be drawn
        # at certain slider position
        # all items that are always visible have True value
        visibility = [True] * len(self.fig.data)

        last_idx = len(self.fig.data) - 1
        for iterable in self.iterables:
            for i, d in enumerate(iterable):
                d.draw(go, self.fig)
                idx = len(self.fig.data) - 1
                drawn = idx - last_idx

                for _ in range(drawn):
                    visibility.append(i)

                last_idx = idx

        steps = []
        for i in range(self.max_iterables):
            step = dict(
                method="restyle",
                args=[{"visible": [v is True or v == i for v in visibility]}],
            )
            steps.append(step)

        generation = dict(
            active=0,
            steps=steps
        )
        self.fig.update_layout(
            sliders=[generation]
        )
        for i, d in enumerate(self.fig.data):
            d.visible = steps[generation['active']]['args'][0]['visible'][i]

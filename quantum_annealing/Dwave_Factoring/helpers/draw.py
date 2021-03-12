# Copyright 2020 D-Wave Systems Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import sys
import math

from bokeh.io import show, output_notebook
from bokeh.models import (
    Plot, Range1d, MultiLine, Circle, HoverTool,
    TapTool, BoxSelectTool, Row, LabelSet, ColumnDataSource
)
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes
from bokeh.palettes import Spectral4
from bokeh.plotting import figure

# call output_notebook once on import, so we don't reload bokeh every time.
me = sys.modules[__name__]
if not hasattr(me, 'bokeh_loaded'):
    output_notebook()
    bokeh_loaded = True

def circuit_layout(G=None):
    pos = {
        'a0': (0.0, 1.0),
        'a1': (0.0, 0.85),
        'a2': (0.0, 0.6),
        'b0': (0.1, 0.4),
        'b1': (0.1, 0.2),
        'b2': (0.1, 0.0),

        'p0':    (1.0, 1.0),
        'and0,1': (0.8, 0.9),
        'and1,0': (0.6, 0.85),
        'and2,0': (0.6, 0.7),
        'and0,2': (0.4, 0.6),
        'and1,1': (0.2, 0.55),
        'and1,2': (0.2, 0.3),
        'and2,1': (0.4, 0.2),
        'and2,2': (0.6, 0.0),

        'p1':      (1.0, 0.85),
        'carry1,0': (0.8, 0.7),
        'sum1,1':   (0.6, 0.55),
        'carry1,1': (0.4, 0.4),

        'p2':      (1.0, 0.6),
        'carry2,0': (0.8, 0.55),
        'sum2,1':   (0.6, 0.4),
        'carry2,1': (0.6, 0.2),

        'p3':      (1.0, 0.4),
        'carry3,0': (0.8, 0.3),

        'p4': (1.0, 0.2),
        'p5': (1.0, 0.0),
    }
    return pos


def add_labels(plot):
    positions = circuit_layout()
    data = {
        'xpos': [],
        'ypos': [],
        'label': []
    }
    for label, pos in positions.items():
        data['label'].append(label)
        data['xpos'].append(pos[0])
        data['ypos'].append(pos[1])

    labels = LabelSet(x='xpos', y='ypos', text='label',
                      level='glyph', source=ColumnDataSource(data),
                      x_offset=-5, y_offset=10, text_color="#F5F7FB", text_font_size='12pt')
    plot.add_layout(labels)


def circuit_from(bqm):
    G = bqm.to_networkx_graph()
    plot = Plot(plot_width=600, plot_height=400,
                x_range=Range1d(-0.1, 1.1), y_range=Range1d(-.1, 1.1))
    plot.title.text = "Multiplication as a BQM"
    plot.add_tools(HoverTool(tooltips=None), TapTool(), BoxSelectTool())
    graph_renderer = from_networkx(G, circuit_layout)

    circle_size = 25
    graph_renderer.node_renderer.glyph = Circle(
        size=circle_size, fill_color="#F5F7FB")
    graph_renderer.node_renderer.selection_glyph = Circle(size=circle_size, fill_color="#EEA64E")
    graph_renderer.node_renderer.hover_glyph = Circle(size=circle_size, fill_color="#FFE86C")

    edge_size = 2
    graph_renderer.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=edge_size)
    graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color="#EEA64E", line_width=edge_size)
    graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color="#FFE86C", line_width=edge_size)

    graph_renderer.selection_policy = NodesAndLinkedEdges()
    graph_renderer.inspection_policy = NodesAndLinkedEdges()

    plot.renderers.append(graph_renderer)

    plot.background_fill_color = "#202239"

    add_labels(plot)
    show(Row(plot))


def frequency_of(results):
    x_range = [str(x) for x in results.keys()]

    p = figure(x_range=x_range, plot_height=250,
               title='Frequency of samples', toolbar_location=None, tools="")
    p.vbar(x=x_range, top=list(results.values()), width=0.9)

    p.xgrid.grid_line_color = None
    p.y_range.start = 0

    show(p)

def energy_of(results):
    x_range = [str(x) for x in results.keys()]

    p = figure(x_range=x_range, plot_height=250,
            title='Energy of samples', toolbar_location=None, tools="")
    p.scatter(x_range, list(results.values()))

    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = math.pi/2

    show(p)

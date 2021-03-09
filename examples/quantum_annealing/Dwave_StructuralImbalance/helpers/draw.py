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

from collections import defaultdict
from itertools import product

import networkx as nx

from bokeh.io import show, output_notebook
from bokeh.models import (
    Plot, Range1d, MultiLine, Circle, HoverTool, WheelZoomTool, ZoomInTool, ZoomOutTool, PanTool,
    Row, LabelSet, ColumnDataSource
)
from bokeh.models.graphs import from_networkx, EdgesAndLinkedNodes


# call output_notebook once on import, so we don't reload bokeh every time.
me = sys.modules[__name__]
if not hasattr(me, 'bokeh_loaded'):
    output_notebook()
    bokeh_loaded = True


def draw(S, position=None, with_labels=False):
    """Plot the given signed social network.

    Args:
        S: The network
        position (dict, optional):
            The position for the nodes. If no position is provided, a layout will be calculated. If the nodes have
            'color' attributes, a Kamanda-Kawai layout will be used to group nodes of the same color together.
            Otherwise, a circular layout will be used.

    Returns:
        A dictionary of positions keyed by node.

    Examples:
    >>> import dwave_structural_imbalance_demo as sbdemo
    >>> gssn = sbdemo.GlobalSignedSocialNetwork()
    >>> nld_before = gssn.get_node_link_data('Syria', 2013)
    >>> nld_after = gssn.solve_structural_imbalance('Syria', 2013)
    # draw Global graph before solving; save node layout for reuse
    >>> position = sbdemo.draw('syria.png', nld_before)
    # draw the Global graph; reusing the above layout, and calculating a new grouped layout
    >>> sbdemo.draw('syria_imbalance.png', nld_after, position)
    >>> sbdemo.draw('syria_imbalance_grouped', nld_after)

    """

    # we need a consistent ordering of the edges
    edgelist = S.edges()
    nodelist = S.nodes()

    def layout_wrapper(S):
        pos = position
        if pos is None:
            try:
                # group bipartition if nodes are colored
                dist = defaultdict(dict)
                for u, v in product(nodelist, repeat=2):
                    if u == v:  # node has no distance from itself
                        dist[u][v] = 0
                    elif nodelist[u]['color'] == nodelist[v]['color']:  # make same color nodes closer together
                        dist[u][v] = 1
                    else:  # make different color nodes further apart
                        dist[u][v] = 2
                pos = nx.kamada_kawai_layout(S, dist)
            except KeyError:
                # default to circular layout if nodes aren't colored
                pos = nx.circular_layout(S)
        return pos
    # call layout wrapper once with all nodes to store position for calls with partial graph
    position = layout_wrapper(S)

    plot = Plot(plot_width=600, plot_height=400, x_range=Range1d(-1.2, 1.2), y_range=Range1d(-1.2, 1.2))
    tools = [WheelZoomTool(), ZoomInTool(), ZoomOutTool(), PanTool()]
    plot.add_tools(*tools)
    plot.toolbar.active_scroll = tools[0]

    def get_graph_renderer(S, line_dash):
        # we need a consistent ordering of the edges
        edgelist = S.edges()
        nodelist = S.nodes()

        # get the colors assigned to each edge based on friendly/hostile
        sign_edge_color = ['#87DACD' if S[u][v]['sign'] == 1 else '#FC9291' for u, v in edgelist]

        # get the colors assigned to each node by coloring
        try:
            coloring_node_color = ['#4378F8' if nodelist[v]['color'] else '#FFE897' for v in nodelist]
        except KeyError:
            coloring_node_color = ['#FFFFFF' for __ in nodelist]

        graph_renderer = from_networkx(S, layout_wrapper)

        circle_size = 10
        graph_renderer.node_renderer.data_source.add(coloring_node_color, 'color')
        graph_renderer.node_renderer.glyph = Circle(size=circle_size, fill_color='color')

        edge_size = 2
        graph_renderer.edge_renderer.data_source.add(sign_edge_color, 'color')
        try:
            graph_renderer.edge_renderer.data_source.add([S[u][v]['event_year'] for u, v in edgelist], 'event_year')
            graph_renderer.edge_renderer.data_source.add(
                [S[u][v]['event_description'] for u, v in edgelist], 'event_description')
            plot.add_tools(HoverTool(tooltips=[("Year", "@event_year"), ("Description", "@event_description")],
                                    line_policy="interp"))
        except KeyError:
            pass
        graph_renderer.edge_renderer.glyph = MultiLine(line_color='color', line_dash=line_dash)

        graph_renderer.inspection_policy = EdgesAndLinkedNodes()

        return graph_renderer

    try:
        S_dash = S.edge_subgraph(((u, v) for u, v in edgelist if S[u][v]['frustrated']))
        S_solid = S.edge_subgraph(((u, v) for u, v in edgelist if not S[u][v]['frustrated']))
        plot.renderers.append(get_graph_renderer(S_dash, 'dashed'))
        plot.renderers.append(get_graph_renderer(S_solid, 'solid'))
    except KeyError:
        plot.renderers.append(get_graph_renderer(S, 'solid'))



    plot.background_fill_color = "#202239"

    positions = layout_wrapper(S)
    if with_labels:
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

    show(Row(plot))

    return positions

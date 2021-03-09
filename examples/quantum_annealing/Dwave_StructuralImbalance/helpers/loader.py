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

import csv
import os
import datetime

import networkx as nx


def global_signed_social_network():
    """Return the global network for the Militant's Mapping Project.

    Reference:
        Mapping Militant Organizations, Stanford University, last modified
        February 28, 2016, http://web.stanford.edu/group/mappingmilitants/cgi-bin/.

    Examples:
        >>> import dwave_structural_imbalance_demo as sbdemo
        >>> Global = global_signed_social_network()
        >>> Global.nodes[1]['map']
        'Aleppo'
        >>> Global[1][671]['event_description']
        'Firqat al-Sultan Murad targets the Islamic State.'

    """
    # create a new empty graph for everything
    S = nx.Graph()

    current_directory = os.path.dirname(__file__)

    links_file = os.path.join(current_directory, 'links.csv')
    with open(links_file, 'r', encoding="utf8") as links:
        data_iter = csv.reader(links, delimiter=',')

        # skip descriptions line
        next(data_iter)

        for row in data_iter:
            assert len(row) == 6

            # get the data by field in the row
            id_, type_, u, v, date, description = row

            # cast the group ids to integers for easier reading
            u, v = int(u), int(v)

            # no self loops in a signed social network
            if u == v:
                continue

            # get the date of the event
            year, month, day = map(int, date.split('-'))
            if month == 0:
                month = 1
            if day == 0:
                day = 1
            dateinfo = datetime.date(year, month, day)

            # fill out the datafield
            data = {'event_id': id_,
                    'event_type': type_,
                    'event_year': int(year), # whole date isn't needed
                    'event_description': description}

            # finally cast the different relation types to either hostile (sign=-1)
            # or friendly (sign=1)
            if type_ == 'riv':
                S.add_edge(u, v, sign=-1, **data)
            elif type_ == 'all' or type_ == 'aff' or type_ == 'spl' or type_ == 'mer':
                S.add_edge(u, v, sign=1, **data)
            else:
                raise ValueError('unexpected relation type "{}"'.format(type_))

    # we are also interested in which region each group operates
    maps_file = os.path.join(current_directory, 'maps.csv')
    map_id_to_name = {}
    with open(maps_file, 'r') as maps:
        data_iter = csv.reader(maps, delimiter=',')
        next(data_iter)  # skip descriptions line

        for map_id, __, map_name, description, __, __, __, __ in data_iter:
            map_id_to_name[map_id] = map_name
    groups_file = os.path.join(current_directory, 'map_groups.csv')
    with open(groups_file, 'r') as groups:
        data_iter = csv.reader(groups, delimiter=',')
        next(data_iter)  # skip descriptions line

        for __, map_id, group_id, __, __, __ in data_iter:
            try:
                map_name = map_id_to_name[map_id]
            except KeyError:
                map_name = map_id

            group_id = int(group_id)

            if group_id in S:
                S.nodes[group_id]['map'] = map_name

    return S

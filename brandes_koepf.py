#  Copyright (c) 2021 Jan Westerhoff
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import copy
from collections import defaultdict
from copy import deepcopy
from enum import Flag, auto
from math import floor, ceil, inf
from multiprocessing import Process
from pathlib import Path
from typing import Union, Optional

import networkx as nx
from matplotlib import pyplot as plt


class Direction(Flag):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class Layer:
    def __init__(self):
        # Enthält die selben Daten und dienen nur des schnellen Zugriffs jenach Key
        self.nodes = dict()
        self.positions = dict()
        self.len = 0

    # def move(self, pos: int, item: str) -> None:
    #     old_node = self.nodes[pos]
    #
    #     # Node, welche nach rechts bewegt werden müssen
    #     temp_dict = dict()
    #     for node in self.nodes.values():
    #         if i := self.positions[node] >= self.positions[old_node]:
    #             self.positions[node] = i + 1
    #             temp_dict[i + 1] = node
    #     self.nodes.update(temp_dict)
    #
    #     self.positions[item] = pos
    #     self.nodes[pos] = item

    def append(self, item):
        self.len += 1
        self.nodes[self.len] = item
        self.positions[item] = self.len

        return self.len

    def pos(self, item):
        return self.positions[item]

    def predecessor(self, item):
        pos = self.positions[item]
        if pos > 1:
            return self.nodes[pos - 1]
        raise ValueError('Für das erste Element gibt es keinen Vorfolger')

    def node_by_index(self, i: int) -> str:
        return self.nodes[i]

    # def set_node_by_index(self, i: int, value) -> None:
    #     self.nodes[i] = value

    def sort(self, G):
        s_list = sorted(self.nodes.values(), key=lambda node: G.nodes[node]['x'])

        self.nodes.clear()
        self.positions.clear()
        for i, node in enumerate(s_list):
            self.nodes[i + 1] = node
            self.positions[node] = i + 1

    def __len__(self):
        return self.len

    def __getitem__(self, item):
        # FIX: Brainfuck 2.0
        return self.nodes[item]

    def __setitem__(self, key, value):
        # FIX: Brainfuck
        if key in self.positions:
            index = self.positions[key]
        else:
            self.len += 1
            index = self.len

        self.nodes[index] = value


class Layout:
    def __init__(self):
        self.layer = defaultdict(Layer)
        self.index = dict()
        self.node_to_layer = dict()

        self.marked_segments = defaultdict(lambda: False)

        self.root = dict()
        self.align = dict()
        self.sink = dict()
        self.shift = dict()
        self.x = defaultdict(lambda: None)

    def add_node(self, layer, node):
        self.layer[layer].append(node)
        self.index[self.layer[layer]] = layer
        self.node_to_layer[node] = layer

    def mark_segement(self, edge):
        self.marked_segments[edge] = True

    def is_marked(self, edge):
        return self.marked_segments[edge]

    def normalize_and_sort(self, G):
        keys = list(self.layer.keys())
        min_layer = min(keys) - 1

        old = copy.copy(self.layer)
        self.layer.clear()
        self.index.clear()

        for key in keys:
            layer = old[key]

            layer.sort(G)

            self.layer[key - min_layer] = layer
            self.index[layer] = key - min_layer

        for key in self.node_to_layer:
            self.node_to_layer[key] -= min_layer

    def pos(self, node):
        return self.layer[self.node_to_layer[node]].pos(node)

    def get_layer(self, node):
        return self.layer[self.node_to_layer[node]]

    def L(self, i):
        return self.layer[i]

    def __len__(self):
        return len(self.layer)

    def __getitem__(self, item):
        return self.layer[item]


def list_upper_neighbors(G, layers, i, k, direction):
    if direction.DOWN in direction:
        return sorted([u for u, v in G.in_edges(layers[i].node_by_index(k))],
                      key=lambda n: layers.pos(n))
    else:
        return sorted([v for u, v in G.out_edges(layers[i].node_by_index(k))],
                      key=lambda n: layers.pos(n))


def algo_1(G, layers):
    # ----Algo. 1.------------------------
    for i in range(2, len(layers) - 1):
        k0 = 0
        l = 1
        for l1 in range(1, len(layers[i + 1]) + 1):
            inner_nodes = [(u, v) for u, v in G.in_edges(layers[i + 1][l1]) if "d" in u and "d" in v]
            if l1 == len(layers[i + 1]) or inner_nodes:
                k1 = len(layers[i])
                if inner_nodes:
                    vl1i1 = layers[i + 1][l1]
                    upper_neighbor, _ = inner_nodes[0]
                    k1 = layers.pos(upper_neighbor)
                while l < l1:
                    for vk, vl in G.in_edges(layers[i + 1][l]):
                        k = layers.pos(vk)
                        if k < k0 or k > k1:
                            layers.mark_segement((vk, vl))

                    l += 1
                k0 = k1
    return layers


def algo_2(G, layout: Layout, direction): # Vertical Alignment
    ver_range = range(1, len(layout))

    if Direction.UP in direction:
        ver_range = reversed(ver_range)

    # ----Algo. 2.------------------------
    for i in ver_range:
        if Direction.UP in direction:
            r = 0
        else:
            r = inf
        
        hoz_range = range(1, len(layout[i]))
        sign = 1
        
        if Direction.LEFT in direction:
            hoz_range = reversed(hoz_range)
            sign = -1

        for k in hoz_range:
            upper_neighbors = list_upper_neighbors(G, layout, i, k, direction)
            if upper_neighbors:
                f = floor(((len(upper_neighbors) + 1) / 2))
                c = ceil(((len(upper_neighbors) + 1) / 2))

                vk = layout[i].node_by_index(k)
                for m in [f, c]:
                    if layout.align[vk] == vk:
                        um = upper_neighbors[m - 1]

                        if Direction.LEFT in direction:
                            edge = (vk, um)
                        else:
                            edge = (um, vk)

                        if not layout.is_marked(edge) and (r * sign < sign * layout.pos(um)):
                            layout.align[um] = vk
                            layout.root[vk] = layout.root[um]
                            layout.align[vk] = layout.root[vk]
                            r = layout.pos(um)
    return layout


def algo_3(G, layout, delta, direction): # Horizontal Compaction
    # ----Algo. 3.------------------------
    def place_block(v):
        if layout.x[v] is None:
            layout.x[v] = 0
            w = v
            while True:
                if layout.pos(w) > 1:
                    u = layout.root[layout.get_layer(w).predecessor(w)]
                    place_block(u)
                    if layout.sink[v] == v:
                        layout.sink[v] = layout.sink[u]
                    if layout.sink[v] != layout.sink[u]:
                        layout.shift[layout.sink[u]] = min(layout.shift[layout.sink[u]],
                                                           layout.x[v] - layout.x[u] - delta)
                    else:
                        layout.x[v] = max(layout.x[v], layout.x[u] + delta)
                w = layout.align[w]
                if w == v:
                    break

    for v in G.nodes:
        if layout.root[v] == v:
            place_block(v)

    for v in G.nodes:
        layout.x[v] = layout.x[layout.root[v]]
        if layout.shift[layout.sink[layout.root[v]]] < inf:
            layout.x[v] += layout.shift[layout.sink[layout.root[v]]]

        G.nodes[v]['x'] = layout.x[v]

    # ------------------------------------
    return layout


def brandes_koepf(G, delta=1.0): # Horizontal Coordinate Assignment
    original_layout = Layout()

    # Add Node in to the layers datastructurs
    for node in G.nodes:
        original_layout.add_node(G.nodes[node]['y'], node)
        original_layout.root[node] = node
        original_layout.align[node] = node
        original_layout.sink[node] = node
        original_layout.shift[node] = inf

    directions = [Direction.UP | Direction.LEFT, Direction.UP | Direction.RIGHT, Direction.DOWN | Direction.LEFT,
                  Direction.DOWN | Direction.RIGHT]
    layouts = []
    original_layout.normalize_and_sort(G)
    original_layout = algo_1(G, original_layout)

    i = 0

    for direction in directions:
        l = deepcopy(original_layout)

        l = algo_2(G, l, direction)
        l = algo_3(G, l, delta, direction)

        #print_result(G, path.joinpath(f'{i}.png'))
        i += 1
        layouts.append(l)

    # for layer in

    # width = []
    # minimum = []
    # shift = []
    # minWidthLayout = 0
    #
    # for i, layout in enumerate(layouts):
    #     minimum.append(inf)
    #
    #     width.append(layout.size())
    #     if width[minWidthLayout] > width[i]:
    #         minWidthLayout = i
    #
    #     for l in range(1, len(layout) + 1):
    #         for n in range(1, len(layout[l]) + 1):
    #             node = layout[l].node_by_index(n)
    #             minimum[i] = min(minimum[i], layout.x[node])
    #
    # for i, layout in enumerate(layouts):
    #     shift.append(minimum[minWidthLayout] - minimum[i])
    #
    for node in G.nodes:
        calc_x = []

        for i, layout in enumerate(layouts):
            x = layout.x[node]
            calc_x.append(x)

        calc_x = sorted(calc_x)
        G.nodes[node]['x'] = (calc_x[1] + calc_x[2]) / 2.0

    return G


"""def _draw_graph(G, path, figsize):
    colors = [G[u][v]['color'] for u, v in G.edges()]

    pos = {}
    for node in G.nodes:
        y = -G.nodes[node]['y']
        x = G.nodes[node]['x']
        pos[node] = (x, y)

    print(f"\rDrawing {path.stem}...", end='')
    plt.figure(figsize=figsize)
    nx.draw(G, pos=pos, edge_color=colors, with_labels=True)

    print(f"\rWriting {path.stem} to file...", end='')
    plt.savefig(path)
    plt.close()


def print_result(G, path, figsize=(50, 10)):
    p = Process(target=_draw_graph, args=(G, path, figsize))
    p.start()


def run(path, graph_key, figsize, use_results=True, delta=1):
    file_name = Path(path).stem

    result_path = Path.cwd().joinpath(f'result/brand_koepf/{Path(path).stem}/{graph_key}/')
    result_path.mkdir(parents=True, exist_ok=True)

    if use_results:
        G = gs.load_results(path, graph_key)
    else:
        G = gh.load_file(path, key=graph_key)

    print_result(G, result_path.joinpath(f'{file_name}_before.png'))

    print(f"\rLayer assignment and crossing reduction | {graph_key}", end='')
    G = _brand_koepf(G, file_name, result_path, delta=delta)
    print("\rx-coordinate assigment...", end='')

    print_result(G, result_path.joinpath(f'{file_name}_after.png'))

    nx.readwrite.write_gpickle(G, result_path.joinpath('graph.dat'))
    plt.close()

    print(f"\rDone! {file_name} | {graph_key}", end='\n')"""
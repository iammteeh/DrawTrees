import networkx as nx
import matplotlib.pyplot as plt
import random
from remove_cycles import remove_selfloops, greedy_cycle_removal, revert_edges
from assign_levels import longest_path
from global_sifting import global_sifting

## EXPERIMENTAL STATE

def init_sugiyama(G):
    
    remove_selfloops(G)
    lvl_dict = longest_path(G)
    print(lvl_dict)

    # init positions
    x = 0
    for node in G.nodes:
        nx.set_node_attributes(G, { node: x }, 'x')
        nx.set_node_attributes(G, { node: lvl_dict[node] }, 'y')
        x += 1 # set to distance finally


def run_sugiyama(G):
    node_order = greedy_cycle_removal(G)
    revert_edges(G, node_order)
    return G

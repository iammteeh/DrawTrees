import networkx as nx
import matplotlib.pyplot as plt
import random
from remove_cycles import remove_selfloops, greedy_cycle_removal, revert_edges
from assign_levels import longest_path

def sugiyama(DiGraph):
    remove_selfloops(DiGraph)
    node_order = greedy_cycle_removal(DiGraph)
    revert_edges(DiGraph, node_order)
    return DiGraph

#g = nx.gn_graph(5) # a tree
g = nx.scale_free_graph(50)
nx.draw(g)            
        

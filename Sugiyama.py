import networkx as nx
import matplotlib.pyplot as plt
import random
from remove_cycles import remove_selfloops, greedy_cycle_removal, revert_edges

def sugiyama(DiGraph):
    remove_selfloops(DiGraph)
    node_order = greedy_cycle_removal(DiGraph)
    revert_edges(DiGraph, node_order)
    return DiGraph


def assign_level_by_longest_path(DiGraph):
    m = g.__len__()

    for node, outdegree in g.out_degree:
        if outdegree == 0:
            nx.set_node_attributes(g, { node : m }, 'level')
        else:
            nx.set_node_attributes(g, { node : 'empty' }, 'level')
    
    while any(level == 'empty' for node, level in g.nodes(data='level')): # while not all nodes have assigned a level
        for node, level in g.nodes(data='level'):
            for neighbor in g.neighbors(node):
                neighbors_level = []
                neighbors_level.append(g.nodes[neighbor]['level'])
                if 'empty' not in neighbors_level:
                    n = min(neighbors_level)
                    nx.set_node_attributes(g, { node : n-1 }, 'level')


#g = nx.gn_graph(5) # a tree
g = nx.scale_free_graph(50)
nx.draw(g)            
        

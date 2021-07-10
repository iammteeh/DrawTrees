import networkx as nx

def longest_path(g):
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

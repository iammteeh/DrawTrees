import networkx as nx
import logging

def longest_path(g):
    m = g.__len__()

    for node, outdegree in g.out_degree:
        if outdegree == 0:
            nx.set_node_attributes(g, { node : m }, 'level')
        else:
            nx.set_node_attributes(g, { node : 'empty' }, 'level')
    
    while any(level == 'empty' for node, level in g.nodes(data='level')): # while not all nodes have assigned a level
        logging.info(g.nodes(data='level'))
        for node, level in g.nodes(data='level'):
            logging.debug('node: ' + str(node) + ' level: ' + str(level))
            neighbors_level = []
            logging.debug('neighbors of' + str(node) + ': ' + str(list(g.neighbors(node))))
            for neighbor in g.neighbors(node):
                logging.debug('neighor: ' + str(neighbor))
                neighbors_level.append(g.nodes[neighbor]['level'])
                logging.debug('neighbors levels: ' + str(neighbors_level))
            if 'empty' not in neighbors_level and list(g.neighbors(node)) and level == 'empty':
                logging.debug('neighbors_level empty?' + str(neighbors_level))
                n = min(neighbors_level)
                nx.set_node_attributes(g, { node : n-1 }, 'level')
                logging.debug('assigned level' + str(n-1) + 'to node: ' + str(node))
    logging.info(g.nodes(data='level'))
    return nx.get_node_attributes(g, 'level')

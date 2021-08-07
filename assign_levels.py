import networkx as nx
from main import setup_logger

logger = setup_logger()

def longest_path(g):
    m = g.__len__()

    for node, outdegree in g.out_degree:
        if outdegree == 0:
            nx.set_node_attributes(g, { node : m }, 'level')
        else:
            nx.set_node_attributes(g, { node : 'empty' }, 'level')
    
    while any(level == 'empty' for node, level in g.nodes(data='level')): # while not all nodes have assigned a level
        logger.info(g.nodes(data='level'))
        for node, level in g.nodes(data='level'):
            #logger.debug('node: ' + str(node) + ' level: ' + str(level))
            neighbors_level = []
            #logger.debug('neighbors of' + str(node) + ': ' + str(list(g.neighbors(node))))
            for neighbor in g.neighbors(node):
                #logger.debug('neighor: ' + str(neighbor))
                neighbors_level.append(g.nodes[neighbor]['level'])
                #logger.debug('neighbors levels: ' + str(neighbors_level))
            if 'empty' not in neighbors_level and list(g.neighbors(node)) and level == 'empty':
                #logger.debug('neighbors_level empty?' + str(neighbors_level))
                n = min(neighbors_level)
                nx.set_node_attributes(g, { node : n-1 }, 'level')
                #logger.debug('assigned level' + str(n-1) + 'to node: ' + str(node))
    logger.info(g.nodes(data='level'))
    return nx.get_node_attributes(g, 'level')

import networkx as nx
import random
from remove_cycles import remove_cycles
from assign_levels import longest_path
from global_sifting import GlobalSifting
from brandes_koepf import brandes_koepf
import logging

logger = logging.getLogger('draw graphs')

## EXPERIMENTAL STATE

def Sugiyama(G, distance: int = 1):
    logger.info('remove cycles')
    remove_cycles(G, 'greedy_cycle_removal')
    logger.info('assign levels')
    lvl_dict = longest_path(G)
    logger.info('init positions')
    for node in G.nodes:
        x = 0
        #nx.set_node_attributes(G, { node: x }, 'x')
        nx.set_node_attributes(G, { node: lvl_dict[node] }, 'y')
        x += distance
    logger.info('start global sifting')
    global_sifting = GlobalSifting(G)
    G = global_sifting.run(3) # parameter sets amount of sifting rounds
    logger.info('align and compactify graph')
    G = brandes_koepf(G, 1)
    return G
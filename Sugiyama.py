import networkx as nx
import random
from main import setup_logger
from remove_cycles import remove_cycles
from assign_levels import longest_path
from global_sifting import GlobalSifting
#from brandes_koepf import _brand_koepf

## EXPERIMENTAL STATE

def Sugiyama(G, distance: int = 1):
    remove_cycles(G, 'greedy_cycle_removal')
    lvl_dict = longest_path(G)
    # init positions
    for node in G.nodes:
        x = 0
        #nx.set_node_attributes(G, { node: x }, 'x')
        nx.set_node_attributes(G, { node: lvl_dict[node] }, 'y')
        x += distance
    
    global_sifting = GlobalSifting(G)
    G = global_sifting.run(1) # parameter sets amount of sifting rounds
    #G = _brand_koepf(G, 1)
    return G
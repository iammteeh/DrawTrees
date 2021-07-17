import networkx as nx
import random
import logging
from blockify_graph import blockify_graph, get_block_of_node, upper, lower, get_neighbors_of_node, get_neighbors_of_block, levels
from typing import Dict, List

def global_sifting(G):
    sifting_rounds = 10
    block_list, block_dict = create_ordered_block_list(G)
    assign_pi_to_node(G, block_list, block_dict)
    for p in range(sifting_rounds):
        for block in block_list:
            sifting_step()
    return G

def sifting_step():
    return

def sort_adjacencies(G, block_list, block_dict):
    
    N_minus: Dict[any,List] = dict()
    I_minus: Dict[any,List] = dict()
    N_plus: Dict[any,List] = dict()
    I_plus: Dict[any,List] = dict()
    p: Dict[tuple(any,any),int] = dict()

    # init dict values
    for block in block_list:
        for edge in G.in_edges(upper(block_dict[block])): # for s € {(u,v) € E | v = upper(A)}
            u, v = edge
            s = edge
            N_plus[u] = list()
            I_plus[u] = list()
            I_minus[v] = list()
        for edge in G.out_edges(lower(block_dict[block])): # for s € {(w,x) € E | w = lower(A)}
            w, x = edge
            s = edge
            N_minus[x] = list()
            I_minus[x] = list()
            I_plus[w] = list()
    
    for block in block_list:
        logging.debug('block: ' + str(block))
        for edge in G.in_edges(upper(block_dict[block])): # for s € {(u,v) € E | v = upper(A)}
            # init variables
            u, v = edge
            s = edge
            #logging.debug('s: ' + str(s))
            j = len(N_plus[u])
            #logging.debug('N_plus[u]: ' + str(N_plus[u]))
            #logging.debug('j: ' + str(j))
            # execute insertion logic
            #logging.debug('insert v=' + str(v) + ' to ' + str(N_plus[u]) + ' at pos j=' + str(j))
            N_plus[u].append(v)
            #logging.debug('N_plus[u]: ' + str(N_plus[u]))
            pi_block = get_pi_of_block(block, block_list)
            pi_block_u = get_pi_of_block(get_block_of_node(G, u), block_list)
            #logging.debug('pi_block: ' + str(pi_block) + ' pi_block_u: ' + str(pi_block_u))
            if pi_block < pi_block_u:
                logging.debug('pi_block < pi_block_u: ' + str(pi_block) + ' < ' + str(pi_block_u))
                p[s] = j
            else:
                #logging.debug('insert p[s]=' + str(p[s]) + ' to ' + str(I_plus[u]) + ' at pos j=' + str(j))
                try:
                    I_plus[u].pop(j)
                except:
                    pass
                I_plus[u].insert(j, p[s])
                #logging.debug('I_plus[u]: ' + str(I_plus[u]))
                #logging.debug('insert j=' + str(j) + ' to ' + str(I_minus[v]) + ' at pos p[s]=' + str(p[s]))
                try:
                    I_minus[v].pop(p[s])
                except:
                    pass
                I_minus[v].insert(p[s], j)
                #logging.debug('I_minus[v]: ' + str(I_minus[v]))

        for edge in G.out_edges(lower(block_dict[block])): # for s € {(w,x) € E | w = lower(A)}
            # init variables
            w, x = edge
            s = edge
            j = len(N_minus[x])
            # execute insertion logic
            N_minus[x].append(w)
            pi_block = get_pi_of_block(block, block_list)
            pi_block_x = get_pi_of_block(get_block_of_node(G, x), block_list)
            if pi_block < pi_block_x:
                p[s] = j
            else:
                try:
                    I_minus[x].pop(j)
                except:
                    pass
                I_minus[x].insert(j, p[s])
                try:
                    I_plus[w].pop(p[[s]])
                except:
                    pass
                I_plus[w].insert(p[s], j)

    return N_minus, I_minus, N_plus, I_plus

def create_ordered_block_list(G):
    block_dict = blockify_graph(G)
    block_list = []
    for block in block_dict.keys():
        block_list.append(block)
    # randomize order
    random.shuffle(block_list)
    return block_list, block_dict

def get_pi_of_block(block, block_list):
    return block_list.index(block)

def assign_pi_to_node(G, block_list, block_dict):
    for block in block_list:
        for node in block_dict[block]:
            nx.set_node_attributes(G, { node: block_list.index(block)}, 'pi')


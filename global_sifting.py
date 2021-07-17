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

    for node in G.nodes:
        assign_pi_value(G, block_list, block_dict)

    return G

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

def update_adjacencies(G, block_list, a, b, direction, N_minus, I_minus, N_plus, I_plus):
    i = 0
    j = 0
    z = int()
    if direction == 'in':
        neighbors_direction_a = N_minus[a]
        indices_direction_a = I_minus[a]
        neighbors_direction_b = N_minus[b]
        indices_direction_b = I_minus[b]
        neighbors_opposite_z = N_plus[z]
    elif direction == 'out':
        neighbors_direction_a = N_plus[a]
        neighbors_direction_b = N_plus[b]
        neighbors_direction_b = N_plus[b]
        indices_direction_b = I_plus[b]
        neighbors_opposite_z = N_minus[z]

    while i < len(neighbors_direction_a) and j < len(neighbors_direction_b):
        if get_pi_of_block(get_block_of_node(G, neighbors_direction_a[i]), block_list) < get_pi_of_block(get_block_of_node(G, neighbors_direction_b[j]), block_list):
            i += 1
        elif get_pi_of_block(get_block_of_node(G, neighbors_direction_a[i]), block_list) > get_pi_of_block(get_block_of_node(G, neighbors_direction_b[j]), block_list):
            j += 1
        else:
            z = neighbors_direction_a[i]
            neighbors_opposite_z




def assign_p_dict(G, block, block_dict, direction):
    p = {}
    if direction == 'upper':
        i = 0
        for edge in G.in_edges(upper(block_dict[block])):
            p[(edge[0], edge[1])] = i
            i += 1
        return p
    elif direction == 'lower':
        i = 0
        for edge in G.in_edges(lower(block_dict[block])):
            p[(edge[0], edge[1])] = i
            i += 1
        return p
    else:
        raise Exception('No valid direction given.')


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

def assign_pi_to_block(block_list):
    for block in block_list:


def assign_pi_to_node(G, block_list, block_dict):
    for block in block_list:
        for node in block_dict[block]:
            nx.set_node_attributes(G, { node: block_list.index(block)}, 'pi')


import networkx as nx
import random
import logging
import copy
from blockify_graph import blockify_graph, get_block_of_node, upper, lower, get_neighbors_of_node, get_neighbors_of_block, levels
from typing import Dict, List

def global_sifting(G, sifting_rounds = 10):
    block_list, block_dict = create_ordered_block_list(G)
    assign_pi_to_node(G, block_list, block_dict)
    for p in range(sifting_rounds):
        for block in block_list:
            sifting_step(G, block_list, block_dict, block)
    for node in G.nodes:
        nx.set_node_attributes(G, { node : get_pi_of_block(get_block_of_node(G, node), block_list) }, 'pi')
    return G

def sifting_step(G, block_list, block_dict, block):
    block_list.remove(block)
    block_list.insert(0, block)
    N_minus, I_minus, N_plus, I_plus = sort_adjacencies(G, block_list, block_dict)
    chi = 0
    chi_star = 0
    p_star = 0
    for p in range(1, len(block_list)-1):
        chi = chi + sifting_swap(G, block_dict, block_list, block, block_list[p], N_minus, I_minus, N_plus, I_plus)
        if chi < chi_star:
            chi_star = chi
            p_star = p
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

def sifting_swap(G, block_dict, block_list, A, B, N_minus, I_minus, N_plus, I_plus):
    L = set()
    Delta = 0
    y_attributes = nx.get_node_attributes(G, 'y')
    
    if y_attributes[upper(block_dict[A])] in levels(G, block_dict[B]):
        L.add((y_attributes[upper(block_dict[A])],'in'))
        a = upper(block_dict[A])
    if y_attributes[lower(block_dict[A])] in levels(G, block_dict[B]):
        L.add((y_attributes[lower(block_dict[A])],'out'))
        a = lower(block_dict[A])
    if y_attributes[upper(block_dict[B])] in levels(G, block_dict[A]):
        L.add((y_attributes[upper(block_dict[B])],'in'))
        b = upper(block_dict[B])
    if y_attributes[lower(block_dict[B])] in levels(G, block_dict[A]):
        L.add((y_attributes[lower(block_dict[B])],'out'))
        b = lower(block_dict[B])
    for l, d in L:
        a = None
        for node in block_dict[A]:
            if y_attributes[node] == l:
                a = node
        b = None
        for node in block_dict[B]:
            if y_attributes[node] == l:
                b = node
        if a is None or b is None:
            raise Exception('no nodes with equal level found!')
        Delta = Delta + uswap(G, block_list, a, b, d, N_minus, N_plus)
        update_adjacencies(G, block_list, a, b, d, N_minus, I_minus, N_plus, I_plus)

    swap_A = A
    swap_B = B
    index_A = block_list.index(A)
    index_B = block_list.index(B)
    block_list.remove(B)
    block_list.insert(index_A, swap_B)
    block_list.remove(A)
    block_list.insert(index_B, swap_A)

    # pi(A) += 1
    # pi(B) -= 1

    return Delta

def uswap(G, block_list, a, b, direction, N_minus, N_plus):
    c, i, j = 0
    if direction == 'in':
        neighbors_direction_a = N_minus[a]
        neighbors_direction_b = N_minus[b]
    elif direction == 'out':
        neighbors_direction_a = N_plus[a]
        neighbors_direction_b = N_plus[b]

    r = len(neighbors_direction_a)
    s = len(neighbors_direction_b)

    while i < r and j < s:
        if get_pi_of_block(get_block_of_node(G, neighbors_direction_a[i]), block_list) < get_pi_of_block(get_block_of_node(G, neighbors_direction_b[j]), block_list):
            c = c + (s-j)
            i += 1
        elif get_pi_of_block(get_block_of_node(G, neighbors_direction_a[i]), block_list) > get_pi_of_block(get_block_of_node(G, neighbors_direction_b[j]), block_list):
            c = c - (r-i)
            j += 1
        else:
            c = c + (s-j) - (r-i)
            i += 1
            j += 1
    return c

def update_adjacencies(G, block_list, a, b, direction, N_minus, I_minus, N_plus, I_plus):
    i, j = 0
    z = int()
    if direction == 'in':
        neighbors_direction_a = N_minus[a]
        indices_direction_a = I_minus[a]
        neighbors_direction_b = N_minus[b]
        indices_direction_b = I_minus[b]
        neighbors_opposite_z = N_plus[z]
        indices_opposite_z = I_plus[z]
    elif direction == 'out':
        neighbors_direction_a = N_plus[a]
        indices_direction_a = I_plus[a]
        neighbors_direction_b = N_plus[b]
        indices_direction_b = I_plus[b]
        neighbors_opposite_z = N_minus[z]
        indices_opposite_z = I_minus[z]

    r = len(neighbors_direction_a)
    s = len(neighbors_direction_b)

    while i < r and j < s:
        if get_pi_of_block(get_block_of_node(G, neighbors_direction_a[i]), block_list) < get_pi_of_block(get_block_of_node(G, neighbors_direction_b[j]), block_list):
            i += 1
        elif get_pi_of_block(get_block_of_node(G, neighbors_direction_a[i]), block_list) > get_pi_of_block(get_block_of_node(G, neighbors_direction_b[j]), block_list):
            j += 1
        else:
            z = neighbors_direction_a[i]
            ## swap entries at positions Id(a)[i]and Id(b)[j]in N−d(z)and in I−d(z)
            swap_neighbors = neighbors_opposite_z[neighbors_direction_a[i]]
            swap_indices = indices_opposite_z[indices_direction_a[i]]
            #
            neighbors_opposite_z[neighbors_direction_a[i]] = neighbors_opposite_z[neighbors_direction_b[j]]
            indices_opposite_z[indices_direction_a[i]] = indices_opposite_z[indices_direction_b[j]]
            #
            neighbors_opposite_z[neighbors_direction_b[j]] = swap_neighbors
            indices_opposite_z[indices_direction_b[j]] = swap_indices
            ##
            indices_direction_a[i] = indices_direction_a[i+1]
            indices_direction_b[j] = indices_direction_b[j-1]
            i += 1
            j += 1

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


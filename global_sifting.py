import networkx as nx
import random
import logging
import copy
from blockify_graph import create_ordered_block_list , blockify_graph, upper, lower, get_neighbors_of_node, get_neighbors_of_block, levels
from typing import Dict, List

def assign_pi_to_node(self):
    for block in self.block_list:
        for node in self.block_dict[block]:
            nx.set_node_attributes(self.G, { node: self.block_list.index(block)}, 'pi')
class GlobalSifting:
    def __init__(self, G: nx.DiGraph):
        self.G = G
        self.block_list, self.block_dict = create_ordered_block_list(self.G)
        self.pi_node = assign_pi_to_node(self)
        self.N_minus = dict() # marked for further improvement
        self.I_minus = dict() # marked for further improvement
        self.N_plus = dict() # marked for further improvement
        self.I_plus = dict() # marked for further improvement

    #@property
    def get_pi_of_node(self, node):
        return nx.get_node_attributes(self.G, 'pi')[node]

    #@get_pi_of_node.setter
    def set_pi_of_node(self, node, pi):
        nx.set_node_attributes(self.G, { node : pi }, 'pi')

    #@property
    def get_pi_of_block(self, block):
        return self.block_list.index(block)

    #@property
    def get_block_of_node(self, node):
        return nx.get_node_attributes(self.G, 'block_id')[node]

    #@property
    def get_N_minus_of_node(self, node):
        return self.N_minus[node]

    #@property
    def get_I_minus_of_node(self, node):
        return self.I_minus[node]

    #@property
    def get_N_plus_of_node(self, node):
        return self.N_plus[node]

    #@property
    def get_N_minus_of_node(self, node):
        return self.I_plus[node]

    def run(self, sifting_rounds: int=10):
        for p in range(sifting_rounds):
            logging.info('sifting round: ' + str(p))
            for block in copy.deepcopy(self.block_list): # DEBUG LOOP
                self.block_list = self.sifting_step(self.block_list, block)
        for node in self.G.nodes:
            logging.info('update pi of node: ' + str(node))
            self.set_pi_of_node(node, self.get_pi_of_block(self.get_block_of_node(node)))
        
        for node in self.G.nodes(data='pi'):
            logging.warning('node: ' + str(node) + ' pi: ' + str(node[1]))
            nx.set_node_attributes(self.G, { node: node[1] }, 'x')
        return self.G

    def sifting_step(self, block_list, block):
        logging.info('sifting step for block: ' + str(block))
        self.block_list.remove(block)
        self.block_list.insert(0, block)
        self.sort_adjacencies(block_list)
        chi = 0
        chi_star = 0
        p_star = 0
        for p in range(1, len(block_list)-1):
            chi = chi + self.sifting_swap(block, self.block_list[p]) # marked for further improvement
            if chi < chi_star:
                chi_star = chi
                p_star = p
    
        # move block "A" to position of block on position p_star
        logging.info('move block A: ' + str(block))
        cache_block = self.block_list.index(block)
        index_block_p_star = self.block_list.index(self.block_list[p_star])
        block_list.remove(block)
        block_list.insert(index_block_p_star, block)

        return block_list

    def sort_adjacencies(self, block_list):
        logging.info('sort adjacencies')
        logging.debug('block_list: ' + str(block_list))
        logging.debug('block_dict: ' + str(self.block_dict))
        # for reference
        #N_minus: Dict[any,List] = dict()
        #I_minus: Dict[any,List] = dict()
        #N_plus: Dict[any,List] = dict()
        #I_plus: Dict[any,List] = dict()
        #p: Dict[tuple(any,any),int] = dict()

        p = dict()

        # init dict values
        for block in block_list:
            logging.debug('length block_list:' + str(len(block_list)))
            upper_nodes = []
            lower_nodes = []
            upper_nodes.append(upper(self.block_dict[block]))
            lower_nodes.append(lower(self.block_dict[block]))
            for up in upper_nodes:
                self.N_minus[up] = list()
                self.I_minus[up] = list()
            for low in lower_nodes:
                self.N_plus[low] = list()
                self.I_plus[low] = list()
            for edge in self.G.in_edges(upper(self.block_dict[block])): # for s € {(u,v) € E | v = upper(A)} 
                u, v = edge
                s = edge
                self.N_plus[u] = list() # marked for further improvement
                self.I_plus[u] = list() # marked for further improvement
                self.I_minus[v] = list() # marked for further improvement 
            for edge in self.G.out_edges(lower(self.block_dict[block])): # for s € {(w,x) € E | w = lower(A)}
                w, x = edge
                s = edge
                self.N_minus[x] = list() # marked for further improvement
                self.I_minus[x] = list() # marked for further improvement
                self.I_plus[w] = list() # marked for further improvement
        
        for block in block_list: #
            logging.debug('block: ' + str(block))
            for edge in self.G.in_edges(upper(self.block_dict[block])): # for s € {(u,v) € E | v = upper(A)}
                # init variables
                u, v = edge
                logging.debug('u=' + str(u) + ', v=' + str(v))
                s = edge
                j = len(self.N_plus[u]) # marked for further improvement
                # execute insertion logic
                logging.debug('append N_plus[u]=' + str(self.N_plus[u]) + ' with v=' + str(v))
                self.N_plus[u].append(v)
                logging.debug('N_plus[u] is now: ' + str(self.N_plus[u]))
                pi_block = self.get_pi_of_block(block)
                pi_block_u = self.get_pi_of_block(self.get_block_of_node(u))
                if pi_block < pi_block_u:
                    logging.debug('pi_block < pi_block_u: ' + str(pi_block) + ' < ' + str(pi_block_u))
                    p[s] = j
                else:
                    self.I_plus[u].insert(j, p[s]) # marked for further improvement
                    self.I_minus[v].insert(p[s], j) # marked for further improvement

            for edge in self.G.out_edges(lower(self.block_dict[block])): # for s € {(w,x) € E | w = lower(A)}
                # init variables
                w, x = edge
                s = edge
                j = len(self.N_minus[x]) # marked for further improvement
                # execute insertion logic
                self.N_minus[x].append(w) # marked for further improvement
                pi_block = self.get_pi_of_block(block)
                pi_block_x = self.get_pi_of_block(self.get_block_of_node(x))
                if pi_block < pi_block_x:
                    p[s] = j
                else:
                    self.I_minus[x].insert(j, p[s]) # marked for further improvement
                    self.I_plus[w].insert(p[s], j) # marked for further improvement
        
        logging.debug('length N_minus' + str(len(self.N_minus.keys())))
        logging.debug('length N_plus' + str(len(self.N_plus.keys())))
        
    def sifting_swap(self, A, B):
        logging.info('sifting swap for block A=' + str(A) + ' and Block B=' + str(B))
        L = set()
        Delta = 0
        y_attributes = nx.get_node_attributes(self.G, 'y')
        
        if y_attributes[upper(self.block_dict[A])] in levels(self.G, self.block_dict[B]): # marked for further improvement
            L.add((y_attributes[upper(self.block_dict[A])],'in'))
            a = upper(self.block_dict[A])
        if y_attributes[lower(self.block_dict[A])] in levels(self.G, self.block_dict[B]):
            L.add((y_attributes[lower(self.block_dict[A])],'out'))
            a = lower(self.block_dict[A])
        if y_attributes[upper(self.block_dict[B])] in levels(self.G, self.block_dict[A]):
            L.add((y_attributes[upper(self.block_dict[B])],'in'))
            b = upper(self.block_dict[B])
        if y_attributes[lower(self.block_dict[B])] in levels(self.G, self.block_dict[A]):
            L.add((y_attributes[lower(self.block_dict[B])],'out'))
            b = lower(self.block_dict[B])
        for l, d in L:
            a = None
            for node in self.block_dict[A]:
                if y_attributes[node] == l:
                    a = node
            b = None
            for node in self.block_dict[B]:
                if y_attributes[node] == l:
                    b = node
            if a is None or b is None:
                raise Exception('no nodes with equal level found!')
            Delta = Delta + self.uswap(a, b, d)
            self.update_adjacencies(a, b, d)

        swap_A = A
        swap_B = B
        index_A = self.block_list.index(A) # marked for further improvement
        index_B = self.block_list.index(B) # marked for further improvement
        self.block_list.remove(B) # marked for further improvement
        self.block_list.insert(index_A, swap_B) # marked for further improvement
        self.block_list.remove(A) # marked for further improvement
        self.block_list.insert(index_B, swap_A) # marked for further improvement

        index_A += 1
        index_B -= 1
        self.block_list.remove(A)
        self.block_list.insert(index_A, swap_A)
        self.block_list.remove(B)
        self.block_list.insert(index_B, swap_B)

        return Delta

    def uswap(self, a, b, direction):
        logging.info('uswap for nodes ' + str(a) + ' and ' + str(b) + ' in direction ' + str(direction))
        logging.debug('length block_list:' + str(len(self.block_list)))
        logging.debug('length N_minus' + str(len(self.N_minus.keys())))
        logging.debug('length N_plus' + str(len(self.N_plus.keys())))
        c = 0
        i = 0
        j = 0
        if direction == 'in':
            neighbors_direction_a = self.N_minus[upper(self.block_dict[self.get_block_of_node(a)])] # marked for further improvement
            logging.debug('neighbors_direction_a = ' + str(neighbors_direction_a))
            neighbors_direction_b = self.N_minus[upper(self.block_dict[self.get_block_of_node(b)])] # marked for further improvement
            logging.debug('neighbors_direction_b = ' + str(neighbors_direction_b))
        elif direction == 'out':
            neighbors_direction_a = self.N_plus[lower(self.block_dict[self.get_block_of_node(a)])] # marked for further improvement
            logging.debug('neighbors_direction_a = ' + str(neighbors_direction_a))
            neighbors_direction_b = self.N_plus[lower(self.block_dict[self.get_block_of_node(b)])] # marked for further improvement
            logging.debug('neighbors_direction_b = ' + str(neighbors_direction_b))
        else:
            raise Exception('No valid direction given.')

        r = len(neighbors_direction_a)
        s = len(neighbors_direction_b)

        while i < r and j < s: # marked for further improvement
            if self.get_pi_of_block(self.get_block_of_node(neighbors_direction_a[i])) < self.get_pi_of_block(self.get_block_of_node(neighbors_direction_b[j])):
                c = c + (s-j)
                i += 1
            elif self.get_pi_of_block(self.get_block_of_node(neighbors_direction_a[i])) > self.get_pi_of_block(self.get_block_of_node(neighbors_direction_b[j])):
                c = c - (r-i)
                j += 1
            else:
                c = c + (s-j) - (r-i)
                i += 1
                j += 1
        return c
    
    def update_adjacencies(self, a, b, direction):
        logging.info('update adjacencies for node ' + str(a) + ' and ' + str(b) + ' in direction ' + str(direction))
        i = 0
        j = 0
        z = int()
        if direction == 'in':
            A = upper(self.block_dict[self.get_block_of_node(a)])
            B = upper(self.block_dict[self.get_block_of_node(b)])
            logging.debug('A: ' + str(A))
            logging.debug('B: ' + str(B))
            neighbors_direction_a = self.N_minus[upper(self.block_dict[self.get_block_of_node(a)])] # marked for further improvement
            indices_direction_a = self.I_minus[upper(self.block_dict[self.get_block_of_node(a)])] # marked for further improvement
            neighbors_direction_b = self.N_minus[upper(self.block_dict[self.get_block_of_node(b)])] # marked for further improvement
            indices_direction_b = self.I_minus[upper(self.block_dict[self.get_block_of_node(b)])] # marked for further improvement
        elif direction == 'out':
            A = lower(self.block_dict[self.get_block_of_node(a)])
            B = lower(self.block_dict[self.get_block_of_node(b)])
            logging.debug('A: ' + str(A))
            logging.debug('B: ' + str(B))
            neighbors_direction_a = self.N_plus[lower(self.block_dict[self.get_block_of_node(a)])] # marked for further improvement
            indices_direction_a = self.I_plus[lower(self.block_dict[self.get_block_of_node(a)])] # marked for further improvement
            neighbors_direction_b = self.N_plus[lower(self.block_dict[self.get_block_of_node(b)])] # marked for further improvement
            indices_direction_b = self.I_plus[lower(self.block_dict[self.get_block_of_node(b)])] # marked for further improvement
        else:
            raise Exception('No valid direction given.')

        r = len(neighbors_direction_a)
        s = len(neighbors_direction_b)

        while i < r and j < s: # marked for further improvement
            if self.get_pi_of_block(self.get_block_of_node(neighbors_direction_a[i])) < self.get_pi_of_block(self.get_block_of_node(neighbors_direction_b[j])):
                i += 1
            elif self.get_pi_of_block(self.get_block_of_node(neighbors_direction_a[i])) > self.get_pi_of_block(self.get_block_of_node(neighbors_direction_b[j])):
                j += 1
            else: # marked for further improvement # CHECK TWICE
                
                z = neighbors_direction_a[i] 
                if direction == 'in':
                    neighbors_opposite_z = self.N_plus[lower(self.block_dict[self.get_block_of_node(z)])] # marked for further improvement
                    indices_opposite_z = self.I_plus[lower(self.block_dict[self.get_block_of_node(z)])] # marked for further improvement
                elif direction == 'out':
                    neighbors_opposite_z = self.N_minus[upper(self.block_dict[self.get_block_of_node(z)])] # marked for further improvement
                    indices_opposite_z = self.I_minus[upper(self.block_dict[self.get_block_of_node(z)])] # marked for further improvement
                else:
                    raise Exception('No valid direction given.')

                # swap entries at positions Id(a)[i]and Id(b)[j]in N−d(z)and in I−d(z)
                #logging.debug(str(neighbors_opposite_z) +'length N[z]:' + str(len(neighbors_opposite_z)))
                #logging.debug('length indices_opposite_z: ' + str(len(indices_opposite_z)))

                #swap_neighbors = neighbors_opposite_z[indices_direction_a[i]]
                #swap_indices = indices_opposite_z[indices_direction_a[i]]
                
                #neighbors_opposite_z[indices_direction_a[i]] = neighbors_opposite_z[indices_direction_b[j]]
                #indices_opposite_z[indices_direction_a[i]] = indices_opposite_z[indices_direction_b[j]]
                
                #neighbors_opposite_z[indices_direction_b[j]] = swap_neighbors
                #indices_opposite_z[indices_direction_b[j]] = swap_indices
                
                #indices_direction_a[i] += 1
                #indices_direction_b[j] -= 1 
                #i += 1
                #j += 1
                
                logging.debug(str(neighbors_opposite_z) +'length N[z]:' + str(len(neighbors_opposite_z)))
                pos_a_z = neighbors_opposite_z.index(A)
                logging.debug('pos_a_z: ' + str(pos_a_z))
                pos_b_z = neighbors_opposite_z.index(B)
                logging.debug('pos_b_z: ' + str(pos_b_z))
                logging.debug('length indices_opposite_z: ' + str(len(indices_opposite_z)))

                if pos_a_z < pos_b_z:
                    neighbors_opposite_z.pop(pos_a_z)
                    neighbors_opposite_z.pop(pos_b_z - 1)
                    elem_a = indices_opposite_z.pop(pos_a_z)
                    elem_b = indices_opposite_z.pop(pos_b_z - 1)
                else:
                    neighbors_opposite_z.pop(pos_b_z)
                    neighbors_opposite_z.pop(pos_a_z - 1)
                    elem_a = indices_opposite_z.pop(pos_b_z)
                    elem_b = indices_opposite_z.pop(pos_a_z - 1)

                neighbors_opposite_z.insert(pos_a_z, B)
                neighbors_opposite_z.insert(pos_b_z, A)

                indices_opposite_z.insert(pos_a_z, elem_b)
                indices_opposite_z.insert(pos_b_z, elem_a)

                indices_direction_a[i] += 1
                indices_direction_b[j] -= 1 
                i += 1
                j += 1 
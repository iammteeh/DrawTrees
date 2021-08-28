import copy, random
import networkx as nx
import logging

logger = logging.getLogger('draw graphs')

def create_ordered_block_list(G):
    block_dict = blockify_graph(G)
    block_list = []
    for block in block_dict.keys():
        block_list.append(block)
    # randomize order
    random.shuffle(block_list)
    return block_list, block_dict

def blockify_graph(G):
    for node in G.nodes:
        nx.set_node_attributes(G, { node : False }, 'is_dummy')
        nx.set_node_attributes(G, { node : node }, 'block_id')
        nx.set_node_attributes(G, { node : [node] }, 'block')
        nx.set_node_attributes(G, { node : 'empty' }, 'pi')
    add_dummy_vertices(G)
    block_dict = generate_block_dict(G)

    return block_dict

## init blockification by adding dummy nodes
def add_dummy_vertices(G):
    node_levels = nx.get_node_attributes(G, 'level')
    edges = copy.deepcopy(G.edges)
    debug_counter = 0
    logger.debug('edges: ' + str(edges))
    for edge in edges: # make copy of edges to ensure dict keys don't change in interation
        debug_counter += 1
        logger.debug('counter: ' + str(debug_counter))
        node_level_edge_out = node_levels[edge[0]]
        node_level_edge_in = node_levels[edge[1]]
        span = node_level_edge_in - node_level_edge_out
        logger.debug('span between ' + str(edge[0]) + ' and ' + str(edge[1]) + ' is ' + str(span))
        dummy_counter = 1
        block_list = []
        while span > 1:
            logger.debug('block_list: ' + str(block_list) + ' dummy_counter: ' + str(dummy_counter) + ' span: ' + str(span))
            
            if dummy_counter == 1 and span == 2:
                logger.debug('case dc==1 s==2')
                dummy_node_name = 'd' + str(dummy_counter) + '_' + str(edge[0]) + 'B' + str(edge[1])
                block_list.append(dummy_node_name)
                G.add_node(dummy_node_name, is_dummy=True, level=node_level_edge_out+dummy_counter, y=node_level_edge_out+dummy_counter)
                G.add_edge(edge[0],dummy_node_name)
                G.add_edge(dummy_node_name,edge[1])
                logger.debug('block_list: ' + str(block_list) + ' dummy_counter: ' + str(dummy_counter) + ' span: ' + str(span))
            
            elif dummy_counter == 1 and span > 2:
                logger.debug('case dc==1 s>2')
                dummy_node_name = 'd' + str(dummy_counter) + '_' + str(edge[0]) + 'B' + str(edge[1])
                block_list.append(dummy_node_name)
                G.add_node(dummy_node_name, is_dummy=True, level=node_level_edge_out+dummy_counter, y=node_level_edge_out+dummy_counter)
                G.add_edge(edge[0],dummy_node_name)
                logger.debug('block_list: ' + str(block_list) + ' dummy_counter: ' + str(dummy_counter) + ' span: ' + str(span))
            
            elif dummy_counter > 1 and span > 2:
                logger.debug('case dc>1 s>2')
                dummy_node_predecessor_name = block_list[dummy_counter-2] 
                dummy_node_name = 'd' + str(dummy_counter) + '_' + str(edge[0]) + 'B' + str(edge[1])
                block_list.append(dummy_node_name)
                G.add_node(dummy_node_name, is_dummy=True, level=node_level_edge_out+dummy_counter, y=node_level_edge_out+dummy_counter)
                G.add_edge(dummy_node_predecessor_name,dummy_node_name)
                logger.debug('block_list: ' + str(block_list) + ' dummy_counter: ' + str(dummy_counter) + ' span: ' + str(span))

            elif dummy_counter > 1 and span == 2:
                logger.debug('case dc>1 s==2')
                dummy_node_predecessor_name = block_list[dummy_counter-2] 
                dummy_node_name = 'd' + str(dummy_counter) + '_' + str(edge[0]) + 'B' + str(edge[1])
                block_list.append(dummy_node_name)
                G.add_node(dummy_node_name, is_dummy=True, level=node_level_edge_out+dummy_counter, y=node_level_edge_out+dummy_counter)
                G.add_edge(dummy_node_predecessor_name,dummy_node_name)
                G.add_edge(dummy_node_name,edge[1])
                logger.debug('block_list: ' + str(block_list) + ' dummy_counter: ' + str(dummy_counter) + ' span: ' + str(span))

            else:
                raise Exception('Not all cases covered!')

            span -= 1
            dummy_counter += 1
        
        for dummy in block_list:
            nx.set_node_attributes(G, { dummy: str(edge[0]) + 'B' + str(edge[1])}, 'block_id') # TODO
        
        if node_level_edge_in - node_level_edge_out > 1:
            G.remove_edge(edge[0],edge[1])

    return is_proper(G)

def is_proper(G):
    node_levels = nx.get_node_attributes(G, 'level')
    not_proper = []
    for edge in G.edges:
        node_level_edge_out = node_levels[edge[0]]
        node_level_edge_in = node_levels[edge[1]]
        span = node_level_edge_in - node_level_edge_out
        if span > 1:
            not_proper.append((edge[0],edge[1]))
        if not_proper:
            raise Exception(str(edge) + 'has span' + str(span))
    return G

## generate dictionary of blocks
def get_blocks(G):
    block_ids = []
    for node, block_id in G.nodes(data='block_id'):
        block_ids.append(block_id)
    block_list = list(set(block_ids)) # make distinct list of blocks
    return block_list

def get_nodes_by_block_id(G, block_id):
    node_list = []
    for node, block in G.nodes(data='block_id'):
        if block == block_id:
            node_list.append(node)
    return node_list

def generate_block_dict(G):
    block_dict = {}
    block_list = get_blocks(G)
    logger.debug('block_list: ' + str(block_list))
    for block in block_list:
        #logger.debug('add node_list' + str(get_nodes_by_block_id(G, block)) + 'to block' + str(block))
        block_dict[block] = get_nodes_by_block_id(G, block)
    return block_dict

## access functions 
def get_block_of_node(G, node):
    return nx.get_node_attributes(G, 'block_id')[node]

# upper(block_dict[block_id])
def upper(block):
    return block[0]

# lower(block_dict[block_id])
def lower(block):
    return block[len(block)-1]

def get_neighbors_of_node(G, node, direction): # if a list of nodes is passed a list of edges of these nodes is returned
    if direction == 'in':
        neighbors = []
        for edge in G.in_edges(node):
            neighbors.append(edge[0])
        return neighbors
    elif direction == 'out':
        neighbors = []
        for edge in G.out_edges(node):
            neighbors.append(edge[1])
        return neighbors
    else:
        raise Exception('No valid direction given.')

def get_neighbors_of_block(G, block_dict, block, direction):
    if direction == 'in':
        return get_neighbors_of_node(G, upper(block_dict[block]), 'in')
    elif direction == 'out':
        return get_neighbors_of_node(G, lower(block_dict[block]), 'out')
    else:
        raise Exception('No valid direction given.')

def get_indices_of_block(G, block, direction):
    if direction == 'in':
        i_minus_of_block = []
        logger.debug('lookup for block: ' + str(block))
        for neighbor in get_neighbors_of_block(G, block, 'in'):
            logger.debug('neighbor: ' + str(neighbor))
            neighbors_neighbors = get_neighbors_of_block(G, get_block_of_node(G, neighbor), 'out')
            logger.debug('neighbors_neighbors: ' + str(neighbors_neighbors))
            i_minus_of_block.append(neighbors_neighbors.index(block))
        return i_minus_of_block

    elif direction == 'out':
        i_plus_of_block = []
        for neighbor in get_neighbors_of_block(G, block, 'out'):
            neighbors_neighbors = get_neighbors_of_block(G, get_block_of_node(G, neighbor), 'in')
            i_plus_of_block.append(neighbors_neighbors.index(block))
        return i_plus_of_block


# levels(G, block_dict[block_id])
def levels(G, block):
    level_set = set()
    for node in block:
        level_set.add(G.nodes[node]['level'])
    return level_set
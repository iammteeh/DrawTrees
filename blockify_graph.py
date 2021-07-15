import copy, random
import logging
import networkx as nx

def blockify_graph(G):
    for node in G.nodes:
        nx.set_node_attributes(G, { node : False }, 'is_dummy')
        nx.set_node_attributes(G, { node : node }, 'block_id')
        nx.set_node_attributes(G, { node : [node] }, 'block')
        nx.set_node_attributes(G, { node : 'empty' }, 'pi')
    add_dummy_vertices(G)


def add_dummy_vertices_create_blocklist(G):
    edges_to_add = []
    edges_to_remove = []

    # TODO there was an error with 'dictionary changed size during iteration'
    #  -> could not find it
    #  -> this is the solution
    edges = copy.deepcopy(G.edges)

    block_list = [] # should ideally result in a 'propritary' subgraph where 

    for node in G.nodes:
        block_list.append([node])

    for edge in edges:
        try:
            edge_from, edge_to, weight = edge
        except ValueError:
            edge_from, edge_to = edge

        y_attributes = nx.get_node_attributes(G, 'y')
        child_position_attributes = nx.get_node_attributes(G, 'child_position')
        difference = y_attributes[edge_to] - y_attributes[edge_from]
        if difference != 1:
            G.remove_edge(edge_from, edge_to)
            edges_to_remove.append((edge_from, edge_to))
            node_counter = 1
            current_node = edge_from
            current_block = []
            block_identifier = "dummy" + "_" + edge_from + "_" + edge_to
            while difference > 1:
                new_node_name = str(node_counter) + "_" + block_identifier
                if node_counter == 1:
                    child_position = child_position_attributes[edge_to]
                else:
                    child_position = 0
                G.add_node(new_node_name,
                                    y=y_attributes[edge_from] + node_counter,
                                    name=new_node_name,
                                    child_position=child_position,
                                    is_dummy=True)
                current_block.append(new_node_name)
                edges_to_add.append((current_node, new_node_name))
                G.add_edge(current_node, new_node_name, weight=1)
                current_node = new_node_name
                difference -= 1
                node_counter += 1
                y_attributes = nx.get_node_attributes(G, 'y')
                child_position_attributes = nx.get_node_attributes(G, 'child_position')
            G.add_edge(current_node, edge_to, weight=1)
            block_list.append(current_block)
            nx.set_node_attributes(G, { block_identifier : current_block }, 'block')

    return block_list

def initialize_block_position(G, block_list: []):
    random.shuffle(block_list)

    for block_id, block in nx.get_node_attributes(G, 'block').items():
        nx.set_node_attributes(G, { block_id : get_position_of_block(block_list, block) }, 'pi')

    return block_list

def update_node_x_from_blocklist(G, block_list: []):
    for node in G.nodes:
        node_name = node
        if "dummy" in node:
            node_name = "_".join(node_name.split("_")[1:])
        G.add_node(node, x=block_list.index(G.block_lookup[node_name]))

def get_position_of_block(block_list: [], block: [str]):
    for index in range(len(block_list)):
        if len(block_list[index]) == len(block):
            result = all(map(lambda x, y: x == y, block_list[index], block))
            if result:
                return index

    raise Exception("Position For Block Not Found.")

def get_block_to_node(node: str, block_list: [str]):
    for block in block_list:
        if node in block:
            return block

    raise Exception('Block To Node Not Found')

def upper(block: [str]):
    if "dummy" in block[0]:
        return "1_" + block[0]
    else:
        return block[0]

def lower(block: [str]):
    if "dummy" in block[0]:
        return str(len(block) + 1) + "_" + block[0][2:]
    else:
        return block[0]

def add_dummy_vertices(G):
    node_levels = nx.get_node_attributes(G, 'level')
    edges = copy.deepcopy(G.edges)
    debug_counter = 0
    logging.debug('edges: ' + str(edges))
    for edge in edges: # make copy of edges to ensure dict keys don't change in interation
        debug_counter += 1
        logging.debug('counter: ' + str(debug_counter))
        node_level_edge_out = node_levels[edge[0]]
        node_level_edge_in = node_levels[edge[1]]
        span = node_level_edge_in - node_level_edge_out
        logging.debug('span between ' + str(edge[0]) + ' and ' + str(edge[1]) + ' is ' + str(span))
        dummy_counter = 1
        block_list = []
        while span > 1:
            logging.debug('block_list: ' + str(block_list) + ' dummy_counter: ' + str(dummy_counter) + ' span: ' + str(span))
            
            if dummy_counter == 1 and span == 2:
                logging.debug('case dc==1 s==2')
                dummy_node_name = 'd' + str(dummy_counter) + '_' + str(edge[0]) + 'B' + str(edge[1])
                block_list.append(dummy_node_name)
                G.add_node(dummy_node_name, is_dummy=True, level=node_level_edge_out+dummy_counter, ) # TODO NAMING
                G.add_edge(edge[0],dummy_node_name)
                G.add_edge(dummy_node_name,edge[1])
                logging.debug('block_list: ' + str(block_list) + ' dummy_counter: ' + str(dummy_counter) + ' span: ' + str(span))
            
            elif dummy_counter == 1 and span > 2:
                logging.debug('case dc==1 s>2')
                dummy_node_name = 'd' + str(dummy_counter) + '_' + str(edge[0]) + 'B' + str(edge[1])
                block_list.append(dummy_node_name)
                G.add_node(dummy_node_name, is_dummy=True, level=node_level_edge_out+dummy_counter, ) # TODO
                G.add_edge(edge[0],dummy_node_name)
                logging.debug('block_list: ' + str(block_list) + ' dummy_counter: ' + str(dummy_counter) + ' span: ' + str(span))
            
            elif dummy_counter > 1 and span > 2:
                logging.debug('case dc>1 s>2')
                dummy_node_predecessor_name = block_list[dummy_counter-2] 
                dummy_node_name = 'd' + str(dummy_counter) + '_' + str(edge[0]) + 'B' + str(edge[1])
                block_list.append(dummy_node_name)
                G.add_node(dummy_node_name, is_dummy=True, level=node_level_edge_out+dummy_counter, ) # TODO
                G.add_edge(dummy_node_predecessor_name,dummy_node_name)
                logging.debug('block_list: ' + str(block_list) + ' dummy_counter: ' + str(dummy_counter) + ' span: ' + str(span))

            elif dummy_counter > 1 and span == 2:
                logging.debug('case dc>1 s==2')
                dummy_node_predecessor_name = block_list[dummy_counter-2] 
                dummy_node_name = 'd' + str(dummy_counter) + '_' + str(edge[0]) + 'B' + str(edge[1])
                block_list.append(dummy_node_name)
                G.add_node(dummy_node_name, is_dummy=True, level=node_level_edge_out+dummy_counter, ) # TODO
                G.add_edge(dummy_node_predecessor_name,dummy_node_name)
                G.add_edge(dummy_node_name,edge[1])
                logging.debug('block_list: ' + str(block_list) + ' dummy_counter: ' + str(dummy_counter) + ' span: ' + str(span))

            else:
                raise Exception('Not all cases covered!')

            span -= 1
            dummy_counter += 1
        
        for dummy in block_list:
            nx.set_node_attributes(G, { dummy: str(edge[0]) + 'B' + str(edge[1])}, 'block_id') # TODO
        
        if node_level_edge_in - node_level_edge_out > 1:
            G.remove_edge(edge[0],edge[1])

    return is_proper(G)

def get_blocks(G):
    block_ids = []
    for node, block_id in G.nodes(data='block_id'):
        block_ids.append(block_id)
    block_list = list(set(block_ids))
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
    for node, block_id in G.nodes(data='block_id'):
        block_dict["block_id"] = get_nodes_by_block_id(G, block_id)
    return block_dict

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
import networkx as nx
import copy
import logging

def remove_cycles(DiGraph, method):    
    remove_selfloops(DiGraph)
    if method == 'greedy_cycle_removal':
        node_order = greedy_cycle_removal(DiGraph)
        revert_edges(DiGraph, node_order)
    else:
        raise Exception('No method with this name available!')
    return DiGraph

def remove_selfloops(DiGraph):
    if nx.selfloop_edges(DiGraph):
        for edge_from, edge_to in list(nx.selfloop_edges(DiGraph)):
            DiGraph.remove_edge(edge_from, edge_to)
    else:
        return

def greedy_cycle_removal(DiGraph):
    copy_graph = copy.deepcopy(DiGraph)
    s_1 = []
    s_2 = []
    while len(copy_graph.nodes) != 0:
        sink_counter, sinks = get_sinks(copy_graph)
        while sink_counter != 0:
            sink = sinks.pop(0)
            sink_counter -= 1
            s_2.insert(0, sink)
            copy_graph.remove_node(sink)
            sink_counter, sinks = get_sinks(copy_graph)

        root_counter, roots = get_sources(copy_graph)
        while root_counter != 0:
            root = roots.pop(0)
            root_counter -= 1
            s_1.append(root)
            copy_graph.remove_node(root)
            root_counter, roots = get_sources(copy_graph)

        if len(copy_graph.nodes) != 0:
            max_node = get_node_with_max_degree_ratio(copy_graph)
            s_1.append(max_node)
            copy_graph.remove_node(max_node)

    return s_1 + s_2

## helper functions 
def remove_successor_edges(node, DiGraph):
    for successor in list(DiGraph.successors(node)): # use list() to avoid error of changing dict size during iteration
        logging.debug('remove edge ' + str(node) + ' ' + str(successor))
        DiGraph.remove_edge(node,successor)
        
def remove_predecessor_edges(node, DiGraph):
    for predecessor in list(DiGraph.predecessors(node)): # use list() to avoid error of changing dict size during iteration
        logging.debug('remove edge ' + str(predecessor) + ' ' + str(node))
        DiGraph.remove_edge(predecessor,node)

def get_node_with_max_degree_ratio(DiGraph):
    nodes_degree_ratio = []
    nodes_with_max_ratio = []
    selected_node = None
    for node in DiGraph.nodes:
        d_out = DiGraph.out_degree(node)
        d_in = DiGraph.in_degree(node)
        nodes_degree_ratio.append(d_out - d_in)
    
    NDR = list(zip(DiGraph.nodes,nodes_degree_ratio)) # create tuples of nodes and their degree ratio
    a_node_with_max_ratio = max(list(NDR),key=lambda item:item[1])[0]
    return a_node_with_max_ratio
     
def get_sinks(DiGraph):
    sinks = []
    for node, outdegree in DiGraph.out_degree:
        if outdegree == 0:
            sinks.append(node)
    return len(sinks), sinks

def get_sources(DiGraph):
    sources = []
    for node, indegree in DiGraph.out_degree:
        if indegree == 0:
            sources.append(node)
    return len(sources), sources

## revert edges after greedy cycle removal
def revert_edges(DiGraph, node_order: [list]):
    reverting_edges = []
    reverted_edges = []
    weight = 1

    for edge in DiGraph.edges:
        try:
            edge_from, edge_to, weight = edge
        except ValueError:
            edge_from, edge_to = edge
        if node_order.index(edge_from) < node_order.index(edge_to):
            reverting_edges.append(edge)

    for edge in reverting_edges:
        try:
            edge_from, edge_to, weight = edge
        except ValueError:
            edge_from, edge_to = edge
        DiGraph.remove_edge(edge_from, edge_to)
        DiGraph.add_edge(edge_to, edge_from,  weight=weight)
        reverted_edges.append((edge_to, edge_from))

    return reverted_edges


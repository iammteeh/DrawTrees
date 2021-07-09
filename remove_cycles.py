import networkx as nx
import copy
import logging

def remove_selfloops(DiGraph):
    if nx.selfloop_edges(DiGraph):
        for edge_from, edge_to in list(nx.selfloop_edges(DiGraph)):
            DiGraph.remove_edge(edge_from, edge_to)
    else:
        return

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
    
def analyze_nodes_left(DiGraph):
    nodes_degree_ratio = []
    for node in DiGraph.nodes:
        logging.debug('node: ' + str(node) + ' out degree: ' + str(DiGraph.out_degree(node)) + ' in degree: ' + str(DiGraph.in_degree(node)) + ' ratio: ' + str(DiGraph.out_degree(node) - DiGraph.in_degree(node)))
        

#def greedy_cycle_removal(DiGraph):
#    DiGraph = copy.deepcopy(DiGraph)
#    logging.debug('initial nodes:' + str(DiGraph.nodes))
#    # gen source list
#    sources = []
#    for node, indegree in DiGraph.in_degree:
#        if indegree == 0:
#            sources.append(node)
#    logging.debug('sources:' + str(sources))
#    # gen sink list
#    sinks = []
#    for node, outdegree in DiGraph.out_degree:
#        if outdegree == 0:
#            sinks.append(node)
#    logging.debug('sinks:' + str(sinks))
#    S_l = []
#    S_r = []
#    while DiGraph.__len__() > 0:
#        for source in sources:
#            S_l.append(source)
#            remove_successor_edges(source, DiGraph)
#            logging.debug('remove source node ' + str(source))
#            DiGraph.remove_node(source)
#        # clear sources
#        for source in S_l:
#            try:
#                sources.remove(source)
#            except:
#                pass
#        for sink in sinks:
#            S_r.append(sink)
#            remove_predecessor_edges(sink, DiGraph)
#            logging.debug('remove sink node ' + str(sink))
#            DiGraph.remove_node(sink)
#        # clear sinks
#        for sink in S_r:
#            try:
#                sinks.remove(sink)
#            except:
#                pass
#        for source in S_l:
#            try:
#                sources.remove(source)
#            except:
#                pass
#        if DiGraph.__len__() > 0:
#            logging.debug('nodes left:')
#            analyze_nodes_left(DiGraph)
#            v = get_node_with_max_degree_ratio(DiGraph)
#            logging.debug(v)
#            try:
#                remove_predecessor_edges(v, DiGraph)
#                remove_successor_edges(v, DiGraph)
#            except:
#                logging.debug('no edges to remove')
#            try:
#                DiGraph.remove_node(v)
#            except:
#                logging.debug('node already removed')
#    return S_l + S_r

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


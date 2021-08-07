import newick
from ete3 import Tree
import networkx as nx
import logging

logger = logging.getLogger('draw graphs')
#def newick_to_nx(file):
#    newick.read(file)

## parse with newick
def newick(file):
    return newick.read(file) # returns a list of newick.Node

## parse with ete3
def ete3(file,format):
    return Tree(file,format=format)

## make tree out of graphml forest
def graphml_forest_to_ete3_tree(file):
    g = nx.readwrite.read_graphml(file,node_type=str,edge_key_type=int) # read graphml
    gmltree = Tree() # create ete3 tree object
    components = nx.number_connected_components(g) # get components
    subgraph = [g.subgraph(c).copy() for c in nx.connected_components(g)] # generate subgraphs
    for component in nx.connected_components(g):    # for each component create subtree
        gmltree.add_child(name=component.pop())
    for graph in subgraph:
        for child in nx.dfs_successors(graph):
            gmltree.add_child(name=child.name)
    return gmltree

def parse_graphml_multigraph(file):
    graph = nx.readwrite.read_graphml(file,node_type=str,edge_key_type=str)
    if type(graph) == "<class 'networkx.classes.multigraph.Graph'>" or type(graph) == "<class 'networkx.classes.multigraph.DiGraph'>":
        return graph
    elif type(graph) == "<class 'networkx.classes.multigraph.MultiGraph'>":
        # get subgraphs by data key
        data_keys = []
        for edge in graph.edges(keys=True, data=True):
            # 0: u
            # 1: v
            # 2: index of edge between u and v
            # 3: data key

            for key in edge[3]:
                data_keys.append(key)
        subgraphs = list(set(data_keys)) # make unique item list of data keys

        wrapped_multigraph = {}
        for graph in subgraphs:
            wrapped_multigraph[graph] = nx.DiGraph()
            for edge in g.edges(keys=True, data=True):
                for key in edge[3]:
                    if graph == key:
                        wrapped_multigraph[graph].add_node(edge[0])
                        wrapped_multigraph[graph].add_node(edge[1])
                        wrapped_multigraph[graph].add_edge(edge[0],edge[1])
        return wrapped_multigraph
    else:
        print('Error: Graph type not covered.')
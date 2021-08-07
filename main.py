import os, sys
import logging
from GraphML import GraphML
from DrawTree import assign_tree_layout
from Sugiyama import Sugiyama
import networkx as nx
import matplotlib.pyplot as plt
# SYS
logging_format = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s'
## INPUT
graph_type = 'DiGraph'
input_format = 'graphml'
#string = '((C)A,(D)B)F;' # for newick trees
#file = 'phyliptree.nh' # newick tree data
filepath = './data/Software-Engineering/'
graphlist = [ 'JFtp.graphml', 'JUnit-4.12.graphml', 'Stripes-1.5.7.graphml', 'Checkstyle-6.5.graphml' ] # GraphML MultiGraph data
#graphlist = [' complete7 ']
multigraph_key = 'method-call' # Edge Key

## some nx graphs
# G = nx.gn_graph(5) # a tree
# G = nx.scale_free_graph(50)        

# CUSTOM
show_graph = False
distance = 1

# OUTPUT
scale_x = 200 # figure size x
scale_y = 30 # figure size y
node_color = str()
edge_color = str()

def setup_logger():
    logger = logging.getLogger('draw ' + str(input_format) + ' ' + str(graph_type))
    return logger

def parse_input(input_format, path_to_file, *args):
    if input_format == 'graphml':
        G = GraphML(path_to_file).to_graph(multigraph_key)

    elif input_format == 'test':
        g = nx.complete_graph(7)
        g = nx.to_directed(g)
        G = nx.DiGraph()
        for node in g.nodes:
            G.add_node(node)
        for edge in g.edges:
            G.add_edge(edge[0],edge[1])
    return G

def assign_layout(G, graph_type):
    if graph_type == 'tree':
        pos = assign_tree_layout(G)
        return pos
    elif graph_type == 'DiGraph':
        G = Sugiyama(G)
        x_attributes = nx.get_node_attributes(G, 'x')
        y_attributes = nx.get_node_attributes(G, 'y')
        pos_dict = dict()
        for node in G.nodes:
            pos_dict[node] = (x_attributes[node] * 10, y_attributes[node] * 5)
        return pos_dict

def main():
    # set logging
    logger = setup_logger()
    streamhandler = logging.StreamHandler()
    streamhandler.setLevel(logging.WARNING)
    streamhandler.setFormatter(logging_format)
    logger.addHandler(streamhandler)

    for filename in graphlist:
        filehandler = logging.FileHandler('./output/' + filename + '.log', mode='w')
        filehandler.setLevel(logging.DEBUG)
        filehandler.setFormatter(logging_format)
        logger.addHandler(filehandler)
        path_to_file = filepath + filename
        savefile = './output/' + filename + '.png'

        G = parse_input(input_format, path_to_file, multigraph_key)
        pos = assign_layout(G, graph_type)
        
        # plotting
        plt.figure(1, figsize=(scale_x, scale_y))
        nx.draw(G, pos=pos)
        #plt.gca().invert_yaxis()
        plt.savefig(savefile, format='png', dpi=60)
        print("Figure saved in", savefile)
        if show_graph:
            plt.show()
        plt.clf()

if __name__ == '__main__':
    main()
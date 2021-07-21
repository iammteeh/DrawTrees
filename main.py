import os, sys
import logging
import GraphML
from DrawTree import assign_tree_layout
import Sugiyama
import networkx as nx
import matplotlib.pyplot as plt
# SYS
logging.getLogger().setLevel(logging.WARNING)

## INPUT
graph_type = 'DiGraph'
input_format = 'graphml'
#string = '((C)A,(D)B)F;' # for newick trees
#file = 'phyliptree.nh' # newick tree data
file = './graphml/JFtp.graphml' # GraphML MultiGraph data
multigraph_key = 'method-call' # Edge Key

## some nx graphs
# G = nx.gn_graph(5) # a tree
# G = nx.scale_free_graph(50)        
g = nx.complete_graph(7)
g = nx.to_directed(g)
G = nx.DiGraph()
for node in g.nodes:
    G.add_node(node)
for edge in g.edges:
    G.add_edge(edge[0],edge[1])    
## 

# CUSTOM
distance = 1
scale_x = 10 # figure size x
scale_y = 10 # figure size y
node_color = str()
edge_color = str()
savefile = str()


def parse_input(input_format, file, *multigraph_key):
    if input_format == 'graphml':
        G = GraphML(file).to_graph(multigraph_key)
    return G

def assign_layout(G, graph_type):
    if graph_type == 'tree':
        pos = assign_tree_layout(G)
    elif graph_type == 'DiGraph':
        pos = Sugiyama(G)



def main():
    G = parse_input(input_format, file)
    pos = assign_layout(G, graph_type)
    
    # plotting
    plt.figure(1, figsize=(scale_x, scale_y))
    nx.draw(G, pos=pos, node_color=node_color, edge_color=edge_color, with_labels=True)
    plt.gca().invert_yaxis()
    plt.savefig(savefile, format='png', dpi=300)
    print("Figure saved in", savefile)
    #if show_graph:
    plt.show()
    plt.clf()

if __name__ == '__main__':
    main()
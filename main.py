import os, sys
from os import listdir
from os.path import isfile, join
import threading
import concurrent.futures
import logging
from argparse import ArgumentParser, FileType
import re
from GraphML import GraphML
from ete3 import Tree
from DrawTree import assign_tree_layout
from Sugiyama import Sugiyama
import networkx as nx
import matplotlib.pyplot as plt
# SYS
logging_format = logging.Formatter('%(asctime)s %(msecs)d - %(name)s %(levelname)s - %(message)s')
## INPUT SETTINGS
filepath = './data/'
multigraph_key = 'method-call' # Edge Key

def parse_input():

    # parse arguments to run specified routines
    parser = ArgumentParser(description='select graphtype, input format, single files to visualize or run test')
    parser.add_argument('-A', '--all', action='store_true', dest='complete_run')
    parser.add_argument('-t', '--test', action='store_true', dest='test', default=True)
    parser.add_argument('-f', '--files', action='store', nargs='+', type=FileType('r'), dest='files')

    options = parser.parse_args()
    graphlist = []
    
    if options.complete_run:
        print('perform complete run')
        filelist = [file for file in listdir(filepath) if isfile(join(filepath, file))]
        for file in filelist:
            if re.match('.*\.graphml', file):
                graphml = {}
                graphml['filename'] = file
                graphml['graph'] = GraphML(file).to_graph(multigraph_key) # TODO set argument variable for multigraph key and rm perma key 'method-call'
                graphml['graph_type'] = 'DiGraph'

                graphlist.append(graphml)

            elif re.match('.*\.nh', file):
                newick = {}
                newick['filename'] = file
                newick['graph'] = Tree(file,format=format)
                newick['graph_type'] = 'tree'

                graphlist.append(newick)
            
            else:
                raise Exception('File ' + file + ' has no valid format.')
                pass

        return graphlist

    elif options.files:
        print('run on ' + str(options.files))
        for file in options.files:
            file = str(file.name) # file.name takes the relative path from the entrypoint
            if re.match('.*\.graphml', file):
                graphml = {}
                graphml['filename'] = file
                graphml['graph'] = GraphML(file).to_graph(multigraph_key) # TODO set argument variable for multigraph key and rm perma key 'method-call'
                graphml['graph_type'] = 'DiGraph'

                graphlist.append(graphml)

            elif re.match('.*\.nh', file):
                newick = {}
                newick['filename'] = file
                newick['graph'] = Tree(file,format=format)
                newick['graph_type'] = 'tree'

                graphlist.append(newick)
        return graphlist

    elif options.test:
        print('perform test run')
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

        testgraph = {}
        testgraph['filename'] = 'complete7'
        testgraph['graph'] = G
        testgraph['graph_type'] = 'CompleteDirected'
        graphlist.append(testgraph)

        return graphlist

# CUSTOM
show_graph = False
distance = 1

# OUTPUT SETTINGS
scale_x = 200 # figure size x
scale_y = 30 # figure size y
node_color = str()
edge_color = str()

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

def draw_graph(graph, logger):
    print('run ' + str(graph))
    # add logging handler to output logging in separate file
    filename = graph['filename'].split('/') # split dir from filename

    filehandler = logging.FileHandler('./output/' + filename[1] + '.log', mode='w') # filename[1] takes only the filename
    filehandler.setLevel(logging.DEBUG)
    filehandler.setFormatter(logging_format)
    logger.addHandler(filehandler)
    
    savefile = './output/' + graph['filename'] + '.png'
    
    pos = assign_layout(graph['graph'], graph['graph_type'])
    
    # plotting
    plt.figure(1, figsize=(scale_x, scale_y))
    nx.draw(graph['graph'], pos=pos)
    plt.savefig(savefile, format='png', dpi=60)
    print("Figure saved in", savefile)
    if show_graph:
        plt.show()
    plt.clf()

    # remove handler 
    logger.removeHandler(filehandler)


def main():
    # set logging
    logger = logging.getLogger('draw graphs')
    logger.setLevel(logging.DEBUG)
    streamhandler = logging.StreamHandler()
    streamhandler.setLevel(logging.WARNING)
    streamhandler.setFormatter(logging_format)
    logger.addHandler(streamhandler)

    graphlist = parse_input()
    threads = []
    #for graph in graphlist:
        #current_thread = threading.Thread(target=draw_graph, args=(graph, logger))
        #threads.append(current_thread)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        graphs = {executor.submit(draw_graph, graph, logger): graph for graph in graphlist}
        for graph in concurrent.futures.as_completed(graphs):
            graph = graphs[graph]
            try:
                graph.result()
            except Exception as exc:
                print('couldn\'t finish ' + str(graph))
            else:
                print('finished ' + str(graph))

    #for thread in threads:
        #thread.start()
        #thread.join()

if __name__ == '__main__':
    main()
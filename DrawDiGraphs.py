import networkx as nx
import matplotlib.pyplot as plt


# hierarchical directed graph issues

def assign_level_by_longest_path(DiGraph):
    m = nx.number_of_nodes(DiGraph)
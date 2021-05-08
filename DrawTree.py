#from os import listdir, walk
#from os.path import isfile, join
import inspect
import newick
from ete3 import Tree
import matplotlib.pyplot as plt
import networkx as nx

## parse with newick
def newick(file):
    return newick.read(file) # returns a list of newick.Node

## parse with ete3
def ete3(file,format):
    return Tree(file,format=format)

## init functions
def get_lvl(node):
    lvl = 1
    while (node.is_root() == False):
        lvl += 1
        node = node.up
    return lvl

def induce_order(tree):
    print('inducing order')
    i = 0 # maybe set to 1 initially
    for node in tree.traverse():
        # set depth and index
        node.add_features(depth=get_lvl(node), idx=i)
        #print('set depth=' + str(node.depth) + "and idx=" + str(node.idx) + 'for node ' + str(node.idx))
        # for binary trees
        if len(node.get_children()) == 2:
            node.add_features(left=node.children[0],right=node.children[1])
        # set lmost and rmost sibling for all nodes not leaves
        if not node.is_leaf() or len(node.get_children()) != 0:
            node.add_features(lmost_sibling=node.children[0], rmost_sibling=node.children[len(node.get_children())-1])
        # set features for buchheim
        node.add_features(mod=0, thread=0, shift=0, change=0, prelim_x=0)
        node.add_features(ancestor=node)
        i += 1
    print('successfully induced order')

## some test functions
def left_sibling(node):
    print('get left sibling for ' + str(node.idx))
    left_sibling = False
    if node.up:
        for child in node.up.children:
            if child == node : 
                print('left sibling of ' + str(node.idx) + ' is: ' + str(left_sibling.idx if left_sibling!=False else False))
                return left_sibling
            else: 
                left_sibling = child
    
    print('left sibling of ' + str(node.idx) + ' is: ' + str(child.idx if left_sibling!=False else False))
    return left_sibling
        
def set_lrmost_level(tree):
    for node in tree.traverse():
        return iter(node.depth)

def set_prelim_coords(tree):
    for node in tree.traverse():
        if node.is_leaf(): node.add_features(prelim_x=node.depth)
    #    if len(node.get_children()) == 1 && (node.idx+1 && node.depth ==
##

## buchheim       
def next_left(node):
    if len(node.get_children()) != 0:
        return node.children[0]
    else:
        return node.thread

def next_right(node):
    if len(node.get_children()) != 0:
        return node.children[len(node.get_children())-1]
    else:
        return node.thread
    
def move_subtree(w_minus,w_plus,shift):
    subtrees = w_plus.idx - w_minus.idx
    w_plus.change = w_plus.change - shift / subtrees
    w_plus.shift = w_plus.shift + shift
    w_minus.change = w_minus.change + shift / subtrees
    w_plus.prelim_x = w_plus.prelim_x + shift
    w_plus.mod = w_plus.mod + shift
    
def execute_shifts(node):
    shift = 0
    change = 0
    for children in reversed(node.get_descendants()):
        children.prelim_x += shift
        children.mod += shift
        change += children.change
        shift += children.shift + change
        
def ancestor(v_i_minus,node,default_ancestor):
    if v_i_minus.up in node.up.get_children():
        return v_i_minus.up
    else:
        return default_ancestor

def apportion(node,default_ancestor):
    w = left_sibling(node)
    if w != False:
        v_i_plus = v_o_plus = node
        v_i_minus = w
        v_o_minus = v_i_plus.up.children[0] # left most sibling
        s_i_plus = v_i_plus.mod
        s_o_plus = v_o_plus.mod
        s_i_minus = v_i_minus.mod
        s_o_minus = v_o_minus.mod
        while next_right(v_i_minus) != 0 and next_left(v_i_plus) != 0:
            v_i_minus = next_right(v_i_minus)
            v_i_plus = next_left(v_i_plus)
            v_o_minus = next_left(v_o_minus)
            v_o_plus = next_right(v_o_plus)
            v_o_plus.add_features(ancestor=node)
            shift = (v_i_minus.prelim_x + s_i_minus) - (v_i_plus.prelim_x + s_i_plus) + distance
            if shift > 0:
                move_subtree(ancestor(v_i_minus,node,default_ancestor),node,shift)
                s_i_plus += shift
                s_o_plus += shift
            s_i_minus += v_i_minus.mod
            s_i_plus += v_i_plus.mod
            s_o_minus += v_o_minus.mod
            s_o_plus += v_o_plus.mod
        if next_right(v_i_minus) != 0 and next_right(v_o_plus) == 0:
            v_o_plus.thread = next_right(v_i_minus)
            v_o_plus.mod += s_i_minus - s_o_plus
        if next_left(v_i_plus) != 0 and next_left(v_o_minus) == 0:
            v_o_minus.thread = next_left(v_i_plus)
            v_o_minus.mod += s_i_plus - s_o_minus
            default_ancestor = node
    return default_ancestor
        
def first_walk(node):
    print('start first walk for ' + str(node.idx))
    if node.is_leaf():
        print('reached leaf')
        node.add_features(prelim_x=0)
        print('set prelim_x for ' + str(node.idx))
    else:
        default_ancestor = node.children[0] # left most child
        print('set default ancestor ' + str(default_ancestor.idx))
        for child in node.children:
            print('start first walk for ' + str(child.idx))
            first_walk(child)
            print('start apportion for ' + str(child.idx) + ' with default ancestor ' + str(default_ancestor.idx))
            apportion(child,default_ancestor)
        print('execute shifts for node ' + str(node.idx))
        execute_shifts(node)
        midpoint = 1/2*(node.children[0].prelim_x + node.children[len(node.get_children())-1].prelim_x)
        if left_sibling(node) != False:
            node.add_features(prelim_x=left_sibling(node).prelim_x + distance,mod=node.prelim_x - midpoint)
        else:
            node.add_features(prelim_x=midpoint)

def second_walk(node,m):
    print('write final coordinates for node ' + str(node.idx))
    node.add_features(x=node.prelim_x + m, y=node.depth)
    for child in node.children:
        print('second walk for ' + str(child.idx))
        second_walk(child,m + node.mod)
        
def buchheim(tree):
    print('start buchheim walk')
    induce_order(tree)
    root = tree.get_tree_root()
    print('set root=' + str(root.idx))
    print('start first walk for root ' + str(root.idx))
    first_walk(root)
    print('start second walk for root ' + str(root.idx))
    second_walk(root,-root.prelim_x)
    #return tree
    print('finished')
            
# create nx graph
def DrawTree(tree):
    buchheim(tree)
    print('start drawing')
    NX = nx.Graph()
    for node in tree.traverse():
        NX.add_node(node)
        for children in node:
            NX.add_edge(node, children)
    nx.draw(NX, with_labels=True, font_weight='bold')
# test field
string = '((C)A,(D)B)F;'
file = 'phyliptree.nh'
tree = ete3(file,1) # choose to parse with newick or ete3
distance = 1

print(tree)
buchheim(tree)

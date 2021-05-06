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
    i = 0 # maybe set to 1 initially
    for node in tree.traverse():
        # set depth and index
        node.add_features(depth=get_lvl(node), idx=i)
        # for binary trees
        if len(node.get_children()) == 2:
            node.add_features(left=node.children[0],right=node.children[1])
        # set lmost and rmost sibling for all nodes not leaves
        if not node.is_leaf() or len(node.get_children()) != 0:
            node.add_features(lmost_sibling=node.children[0], rmost_sibling=node.children[len(node.get_children())-1])
        # set features for buchheim
        node.add_features(mod=0, thread=0, shift=0, change=0)
        node.add_features(ancestor=node)
        i += 1

## some test functions
def left_sibling(node):
    left_sibling = None
    if node.up:
        for children in node.up.get_children():
            if children == node : return left_sibling
            else: left_sibling = children
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
    for children in reversed(node):
        children.prelim_x += shift
        children.mod += shift
        change += children.change
        shift = shift + children.shift + change
        
def ancestor(v_i_minus,node,default_ancestor):
    if v_i_minus.up in v.up.get_children():
        return v_i_minus.up
    else:
        return default_ancestor

def has_left_child(node):
    node.idx != node.up.children[0].idx
    node
    
def apportion(node,default_ancestor):
    if left_sibling(node):
        v_i_plus = v_o_plus = node
        v_i_minus = left_sibling(node)
        v_o_minus = v_i_plus.children[0]
        s_i_plus = v_i_plus.mod
        s_o_plus = v_o_plus.mod
        s_i_minus = v_i_minus.mod
        s_o_minus = v_o_minus.mod
        while next_right(v_i_minus) != 0 and next_left(v_i_plus) != 0:
            v_i_minus = next_right(v_i_minus)
            v_i_plus = next_left(v_i_plus)
            v_o_minus = lext_left(v_o_minus)
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
    if next_right(v_i_minus) != 0 and next_right(v_o_plus) = 0:
        v_o_plus.thread = next_right(v_i_minus)
        v_o_plus.mod += s_i_minus - s_o_plus
    if next_left(v_i_plus) != 0 and next_lext(v_o_minus) = 0:
        v_o_minus.thread = next_left(v_i_plus)
        v_o_minus.mod += s_i_plus - s_o_minus
        default_ancestor = node
        
def first_walk(node):
    if node.is_leaf():
        node.add_features(prelim_x=0)
    else:
        default_ancestor = node.children[0]
        for children in node: # TEST
            first_walk(children)
            apportion(children,default_ancestor)
        execute_shifts(node)
        midpoint = 1/2(node.children[0].prelim_x + node.children[len(node.get_children())-1])
        if left_sibling(node):
            node.add_features(prelim_x=left_sibling().prelim_x + distance, \ 
                             mod=node.prelim_x - midpoint)
        else:
            node.add_features(prelim_x=midpoint)

def second_walk(node,m):
    node.add_features(x=node.prelim_x + m, \
                      y=node.depth)
    for children in node:
        second_walk(children,m + node.mod)
            
        
# test field
string = '((C)A,(D)B)F;'
file = 'phyliptree.nh'
tree = ete3(file,1) # choose to parse with newick or ete3
distance = 1
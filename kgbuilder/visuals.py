import networkx as nx
import matplotlib.pyplot as plt

import pandas as pd

import datashader as ds
import datashader.transfer_functions as tf
from datashader.layout import random_layout, circular_layout, forceatlas2_layout
from datashader.bundling import connect_edges, hammer_bundle

from itertools import chain

import scipy

cvsopts = dict(plot_height=400, plot_width=400)

def plot_graph_person_highlighted(G, label_list):
    # Create a circular layout for the graph
    pos = nx.drawing.layout.circular_layout(G)
    # Create a list of node colors, where nodes with a label in label_list will be colored red and the rest will be colored blue
    node_color = ['red' if (v in label_list) else 'blue' for v in G]
    # Create a list of node sizes, where nodes with a label in label_list will be larger than the rest
    node_size =  [500 if (v in label_list) else 35 for v in G]
    # Draw the graph, with specified node colors and sizes, and without displaying node labels
    nx.draw_networkx(G, pos, with_labels = False, node_color=node_color,node_size=node_size)

    # Show the plot
    plt.show()

def convert_to_int_labels(g: nx.Graph) -> nx.Graph:
    mapping = {node: i for i, node in enumerate(g.nodes)}
    g = nx.relabel_nodes(g, mapping)
    return g

def nodesplot(nodes, name=None, canvas=None, cat=None):
    canvas = ds.Canvas(**cvsopts) if canvas is None else canvas
    aggregator=None if cat is None else ds.count_cat(cat)
    agg=canvas.points(nodes,'x','y',aggregator)
    return tf.spread(tf.shade(agg, cmap=["#FF3333"]), px=3, name=name)

def edgesplot(edges, name=None, canvas=None):
    canvas = ds.Canvas(**cvsopts) if canvas is None else canvas
    return tf.shade(canvas.line(edges, 'x','y', agg=ds.count()), name=name)
    
def graphplot(nodes, edges, name="", canvas=None, cat=None):
    if canvas is None:
        xr = nodes.x.min(), nodes.x.max()
        yr = nodes.y.min(), nodes.y.max()
        canvas = ds.Canvas(x_range=xr, y_range=yr, **cvsopts)
        
    np = nodesplot(nodes, name + " nodes", canvas, cat)
    ep = edgesplot(edges, name + " edges", canvas)
    return tf.stack(ep, np, how="over", name=name)

def plot_graph_force_directed(G):
    g=convert_to_int_labels(nx.DiGraph(G))

    nodes = pd.DataFrame([str(i) for i in g.nodes], columns=['name'])
    ledge=[]
    for u,v in g.edges:
        ledge.append([u,v])
    edges = pd.DataFrame(ledge,columns=['source', 'target'])

    forcedirected = forceatlas2_layout(nodes, edges)

    fd_d = graphplot(forcedirected, connect_edges(fd,edges), "Force-directed") 

    tf.Images(fd_d).cols(1)
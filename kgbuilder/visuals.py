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
    # Create a dictionary mapping where each node is mapped to an integer
    mapping = {node: i for i, node in enumerate(g.nodes)}
    # Relabel the nodes of the graph with the integers
    g = nx.relabel_nodes(g, mapping)
    return g

def nodesplot(nodes, name=None, canvas=None, cat=None):
    # Create a canvas object with specified options if none is provided
    canvas = ds.Canvas(**cvsopts) if canvas is None else canvas
    # Create an aggregator for the specified category if provided
    aggregator=None if cat is None else ds.count_cat(cat)
    # Plot the nodes on the canvas using the aggregator
    agg=canvas.points(nodes,'x','y',aggregator)
    # Return the plotted nodes with specified pixel size and name
    return tf.spread(tf.shade(agg, cmap=["#FF3333"]), px=3, name=name)

def edgesplot(edges, name=None, canvas=None):
    # Create a canvas object with specified options if none is provided
    canvas = ds.Canvas(**cvsopts) if canvas is None else canvas
    # Plot the edges on the canvas with a count aggregator
    return tf.shade(canvas.line(edges, 'x','y', agg=ds.count()), name=name)
    
def graphplot(nodes, edges, name="", canvas=None, cat=None):
    # if canvas is None, create a new canvas with the x and y range of the nodes
    if canvas is None:
        xr = nodes.x.min(), nodes.x.max()
        yr = nodes.y.min(), nodes.y.max()
        canvas = ds.Canvas(x_range=xr, y_range=yr, **cvsopts)

    # create a plot for the nodes using the nodesplot function, and append the name " nodes" to the name variable
    np = nodesplot(nodes, name + " nodes", canvas, cat)
    # create a plot for the edges using the edgesplot function, and append the name " edges" to the name variable
    ep = edgesplot(edges, name + " edges", canvas)
    # stack the edges plot and the nodes plot on top of each other and return
    return tf.stack(ep, np, how="over", name=name)

def create_plot_graph_force_directed(G):
    # convert the graph labels to integers
    g=convert_to_int_labels(nx.DiGraph(G))

    # create a dataframe of nodes with a 'name' column
    nodes = pd.DataFrame([str(i) for i in g.nodes], columns=['name'])
    # create a list of edges
    ledge=[]
    for u,v in g.edges:
        ledge.append([u,v])
    # create a dataframe of edges with 'source' and 'target' columns
    edges = pd.DataFrame(ledge,columns=['source', 'target'])

    # create a force-directed layout of the graph
    forcedirected = forceatlas2_layout(nodes, edges)

    # plot the force-directed graph
    force_graph = graphplot(forcedirected, connect_edges(forcedirected,edges), "Force-directed") 

    return force_graph

def create_plot_graph_force_directed_bundled(G):
    # convert the graph labels to integers
    g=convert_to_int_labels(nx.DiGraph(G))

    # create a dataframe of nodes with a 'name' column
    nodes = pd.DataFrame([str(i) for i in g.nodes], columns=['name'])
    # create a list of edges
    ledge=[]
    for u,v in g.edges:
        ledge.append([u,v])
    # create a dataframe of edges with 'source' and 'target' columns
    edges = pd.DataFrame(ledge,columns=['source', 'target'])

    # create a force-directed layout of the graph
    forcedirected = forceatlas2_layout(nodes, edges)

    # plot the force-directed graph
    force_graph = graphplot(forcedirected, hammer_bundle(forcedirected,edges), "Force-directed, bundled") 

    return force_graph

import rdflib
#from rdflib import Graph, Literal, U
#from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph,rdflib_to_networkx_digraph
import networkx as nx

def prune_graph(G, prune_policy):
    to_suppr = []
    for proc in prune_policy:
        to_suppr_temp=[]
        if proc=='deadend':
            # Prune dead-end nodes
            for node in G.nodes:
                if G.in_degree(node) < 2:
                    to_suppr_temp.append(node)
        """if proc=='superfluous':
            # Prune superfluous nodes
            for node in G.nodes:
                for p in patterns:
                    if p in node:
                        to_suppr_temp.append(node)
                        break"""
        if proc=='literals':
            # Prune literals
            for node in G.nodes:
                if not ("http" in node):
                    to_suppr_temp.append(node)
        if proc=='isolated':
            # Prune isolated nodes
            for node in G.nodes:
                if G.in_degree(node) == 0 and G.out_degree(node) == 0:
                    to_suppr_temp.append(node)
        if proc=='apply':
            # Remove again nodes from graph
            for node in to_suppr:
                G.remove_node(node)
            to_suppr = []
        else:
            to_suppr=list(set(to_suppr + to_suppr_temp))

def prune_rdf_graph(G, prune_policy):
    to_suppr = []
    for proc in prune_policy:
        to_suppr_temp = []
        if proc == 'deadend':
            # Prune dead-end nodes
            for node in G.all_nodes():
                if len(list(G.in_edges(node))) < 2:
                    to_suppr_temp.append(node)
        if proc == 'literals':
            # Prune literals
            for node in G.all_nodes():
                if isinstance(node, rdflib.Literal):
                    to_suppr_temp.append(node)
        if proc == 'isolated':
            # Prune isolated nodes
            for node in G.all_nodes():
                if len(list(G.in_edges(node))) == 0 and len(list(G.out_edges(node))) == 0:
                    to_suppr_temp.append(node)
        if proc == 'apply':
            # Remove nodes from graph
            for node in to_suppr:
                G.remove(node)
            to_suppr = []
        else:
            to_suppr = list(set(to_suppr + to_suppr_temp))


def networkx_digraph_to_rdflib_graph(nxgraph):
    """Helper method to convert a networkx Graph/DiGraph/MultiDiGraph to an rdflib Graph."""
    graph = rdflib.Graph()  # Create a new empty rdflib graph to hold the converted data
    for ts, to, data in nxgraph.edges(data=True):  # Iterate over the edges of the networkx graph
        for triples in data['triples']:  # For each edge, iterate over the list of triples associated with the edge
            graph.add(triples)  # Add each triple to the rdflib graph
    return graph  # Return the rdflib graph
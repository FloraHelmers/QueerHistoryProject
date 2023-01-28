import rdflib
from rdflib import Graph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt

import requests
import json

from queries import *


class Endpoint:
    wikidata = "https://query.wikidata.org/sparql"


def get_list_from_sparql(endpoint, query, size=10):

    # Define url and headers for the HTTP request
    endpoint_url = endpoint
    headers = {'User-Agent': 'MyBot'}

    # Define the payload for the GET request
    payload = {
        'query': query+str(size),
        'format': 'json'
    }
    # Make the GET request to the endpoint URL
    r = requests.get(endpoint_url, params=payload, headers=headers)
    results = r.json()

    # Extract the item labels and store in a list
    id_list = [item["person"]["value"].split(
        '/')[-1] for item in results["results"]["bindings"]]

    return id_list


def create_merged_stars_graph(id_list, convert=True):
    # Create an empty RDF graph
    mgraph = Graph()
    # Iterate over the list of nodes (wikidata item ids)
    for node in id_list:
        # Parse the RDF data of the node from the wikidata entity URL in ntriples format
        mgraph.parse(
            'https://www.wikidata.org/wiki/Special:EntityData/'+node+'.nt', format="nt")

    # If the convert parameter is True, the function will convert the RDF graph to a NetworkX multidigraph
    if convert:
        return rdflib_to_networkx_multidigraph(mgraph)
    else:
        return mgraph

def create_people_multigraph(full_graph, node_list):
    G = nx.MultiDiGraph()
    G.add_nodes_from(node_list)

def prune_dead_end(G):
    to_suppr = []

    # Iterate through all nodes in the graph
    for node in G.nodes:
        # Check if the in-degree of the node is less than 2
        if G.in_degree(node) < 2:
            # If it is, add it to the list of nodes to be removed
            to_suppr.append(node)

    # Iterate through the list of nodes to be removed
    for node in to_suppr:
        # Remove the node from the graph
        G.remove_node(node)

def prune_isolated_nodes(G):
    to_suppr = []

    # Iterate through all nodes in the graph
    for node in G.nodes:
        # Check if the in-degree and out-degree of the node are both 0
        if G.in_degree(node) == 0 and G.out_degree(node) == 0:
            # If they are, add the node to the list of nodes to be removed
            to_suppr.append(node)

    # Print the list of nodes to be removed
    print(to_suppr)

    # Iterate through the list of nodes to be removed
    for node in to_suppr:
        # Remove the node from the graph
        G.remove_node(node)

def prune_superfluous_nodes(G, patterns):
    to_suppr = []

    # Iterate through all nodes in the graph
    for node in G.nodes:
        #test if one of the pattern is present in the label of the node
        for p in patterns:
            if p in node:
                # If they are, add the node to the list of nodes to be removed
                to_suppr.append(node)
                break

    # Print the list of nodes to be removed
    print(to_suppr)

    # Iterate through the list of nodes to be removed
    for node in to_suppr:
        # Remove the node from the graph
        G.remove_node(node)

def prune_literals(G):
    to_suppr = []

    # Iterate through all nodes in the graph
    for node in G.nodes:
        if not ("http" in node):
            # If they are a not a link, add the node to the list of nodes to be removed
            to_suppr.append(node)
            break

    # Iterate through the list of nodes to be removed
    for node in to_suppr:
        # Remove the node from the graph
        G.remove_node(node)


def star_merging_pipeline(n, prune_policy):
    l=get_list_from_sparql(Endpoint.wikidata, query_queer_world, size=n)
    G=create_merged_stars_graph(l)
    if prune_policy['remove_deadend']:
        prune_dead_end(G)
    if prune_policy['remove_isolated']:
        prune_isolated_nodes(G)
    return G

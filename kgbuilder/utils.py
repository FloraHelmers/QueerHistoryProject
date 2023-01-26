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

    for node in G.nodes:
        if G.in_degree(node) < 2:
            to_suppr.append(node)

    for node in to_suppr:
        G.remove_node(node)

def prune_isolated_nodes(G):
    to_suppr = []

    for node in G.nodes:
        if G.in_degree(node) == 0 and G.out_degree(node) == 0:
            to_suppr.append(node)

    print(to_suppr)

    for node in to_suppr:
        G.remove_node(node)

def star_merging_pipeline(n, prune_policy):
    l=get_list_from_sparql(Endpoint.wikidata, query_queer_germany, size=n)
    G=create_merged_stars_graph(l)
    if prune_policy['remove_deadend']:
        prune_dead_end(G)
    if prune_policy['remove_isolated']:
        prune_isolated_nodes(G)
    return G

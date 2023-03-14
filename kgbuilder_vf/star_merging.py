import rdflib
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph,rdflib_to_networkx_digraph
import networkx as nx
import matplotlib.pyplot as plt

import requests
import json

from queries import *
from graph_operations import prune_graph


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


def create_merged_stars_graph(id_list, convert="digraph"):
    # Create an empty RDF graph
    mgraph = rdflib.Graph()
    # Iterate over the list of nodes (wikidata item ids)
    for node in id_list:
        # Parse the RDF data of the node from the wikidata entity URL in ntriples format
        mgraph.parse(
            'https://www.wikidata.org/wiki/Special:EntityData/'+node+'.nt', format="nt")

    # If the convert parameter isn't None, the function will convert the RDF graph to the corresponding NetworkX format
    if convert=="digraph":
        return rdflib_to_networkx_digraph(mgraph)
    elif convert=="multidigraph":
        return rdflib_to_networkx_multidigraph(mgraph)
    else:
        return mgraph

def star_merging_pipeline(n, query, prune_policy):
    """
    This function performs a star merging pipeline with the given parameters.

    Args:
        n (int): The number of items to retrieve from the SPARQL query.
        query (str): The SPARQL query string to use.
        prune_policy (str): The policy to use for pruning the merged graph.

    Returns:
        tuple: A tuple containing the merged graph and the list of items retrieved from the SPARQL query.
    """
    l=get_list_from_sparql(Endpoint.wikidata, query, size=n)
    G=create_merged_stars_graph(l)
    prune_graph(G,prune_policy)
    return G,l
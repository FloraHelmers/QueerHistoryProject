#cross-platform methods

import requests
import pandas as pd
import networkx as nx
from queries import Endpoint

def add_viaf_info_to_graph(graph, viaf_id):
    # Construct the VIAF API URL for the given VIAF ID
    viaf_url = Endpoint.viaf+f"/{viaf_id}/justlinks.json"

    # Send a request to the VIAF API and parse the response
    response = requests.get(viaf_url)
    data = response.json()

    # Extract the list of works of art from the response
    works = []
    if 'works' in data:
        works = data['works']
    
    # Add each work of art to the graph
    for work in works:
        # Extract the title and URI of the work of art
        title = work.get('title', {}).get('$')
        uri = work.get('uri')

        # If the work of art has a title and URI, add it to the graph
        if title and uri:
            # Create a new node for the work of art and add it to the graph
            work_node = {'type': 'work', 'uri': uri, 'title': title}
            graph.add_node(uri, **work_node)

            # Add an edge between the person node and the work of art node to indicate that the person created the work of art
            person_uri = Endpoint.viaf+f"/{viaf_id}"
            graph.add_edge(person_uri, uri, type='created')
    
    return graph

def merge_graphs_wd_dbpedia(wd_graph_path, dbpedia_graph_path, crossref_path):
    # Load the Wikidata and DBpedia graphs
    wd_graph = nx.read_gpickle(wd_graph_path)
    dbpedia_graph = nx.read_gpickle(dbpedia_graph_path)

    # Load the cross-reference dataset
    crossref_df = pd.read_csv(crossref_path)

    # Map Wikidata nodes to DBpedia nodes using the cross-reference dataset
    for i, row in crossref_df.iterrows():
        wd_uri = row['WD_URI']
        dbpedia_uri = row['DBPEDIA_URI']
        if wd_uri in wd_graph and dbpedia_uri in dbpedia_graph:
            wd_node = wd_graph.nodes[wd_uri]
            dbpedia_node = dbpedia_graph.nodes[dbpedia_uri]
            wd_node['dbpedia_uri'] = dbpedia_uri
            dbpedia_node['wd_uri'] = wd_uri

    # Combine the graphs
    merged_graph = nx.compose(wd_graph, dbpedia_graph)

    # Combine edge attributes for edges that appear in both graphs
    for u, v, d in merged_graph.edges(data=True):
        if 'wd_uri' in merged_graph.nodes[u] and 'dbpedia_uri' in merged_graph.nodes[v]:
            wd_uri = merged_graph.nodes[u]['wd_uri']
            dbpedia_uri = merged_graph.nodes[v]['dbpedia_uri']
            if wd_uri != dbpedia_uri:
                continue
            dbpedia_data = dbpedia_graph.get_edge_data(v, u)
            wd_data = wd_graph.get_edge_data(u, v)
            if dbpedia_data and wd_data:
                merged_data = {**dbpedia_data, **wd_data}
                merged_graph[u][v] = merged_data

    return merged_graph

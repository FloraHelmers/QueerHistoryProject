import requests
import networkx as nx
import numpy as np

def graph_summary(G):
    # Print basic information about the graph
    print("Number of nodes: ", G.number_of_nodes())
    print("Number of edges: ", G.number_of_edges())
    print("Is directed: ", nx.is_directed(G))
    
    # Calculate and print graph metrics
    print("Density: ", nx.density(G))
    print("Diameter: ", nx.diameter(G))
    print("Average shortest path length: ", nx.average_shortest_path_length(G))
    print("Clustering coefficient: ", nx.average_clustering(G))
    
    # Run PageRank algorithm on the graph and print results
    pr = nx.pagerank(G)
    print("\nPageRank results:")
    for node, score in sorted(pr.items(), key=lambda x: x[1], reverse=True):
        print("Node", node, "has PageRank score", score)

def node_summary(G, node):
    # Check if node exists in the graph
    if node not in G.nodes():
        print("Node not found in graph.")
        return
    
    # Print basic information about the node
    print("Node ID: ", node)
    print("Degree: ", G.degree(node))
    print("Neighbors: ", list(G.neighbors(node)))
    
    # Calculate and print node metrics
    print("Clustering coefficient: ", nx.clustering(G, node))
    print("Betweenness centrality: ", nx.betweenness_centrality(G)[node])
    print("Closeness centrality: ", nx.closeness_centrality(G)[node])
    print("PageRank score: ", nx.pagerank(G)[node])

def top_n_degree_nodes(G, n):
    # Create a dictionary of nodes and their degrees
    degree_dict = dict(G.degree())
    # Sort the dictionary by degree in descending order
    sorted_degree = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)
    # Extract the top n nodes based on degree
    top_n_nodes = [node for node, degree in sorted_degree[:n]]
    return top_n_nodes

def common_neighbors(G, u, v):
    # Get the set of neighbors for node u
    u_neighbors = set(G.neighbors(u))
    # Get the set of neighbors for node v
    v_neighbors = set(G.neighbors(v))
    # Find the intersection of the two sets to get the common neighbors
    common_neighbors = u_neighbors.intersection(v_neighbors)
    return common_neighbors

def get_incoming_properties(G, node):
    # Find all incoming edges to the given node
    incoming_triples = [data for source, target, data in G.in_edges(node, data=True)]
    
    # Return the list of incoming properties with labels
    return [triple[1] for triple in incoming_triples]

def get_entity_summary(entity_id):
    query = """
    SELECT DISTINCT ?propLabel ?valueLabel WHERE {{
      wd:{entity_id} ?p ?value.
      ?prop wikibase:directClaim ?p.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """.format(entity_id=entity_id)

    response = requests.get('https://query.wikidata.org/sparql', params={'query': query, 'format': 'json'})
    data = response.json()

    summary = {}
    categories = set()
    for item in data['results']['bindings']:
        prop = item['propLabel']['value']
        value = item['valueLabel']['value']
        if prop == "instance of":
            categories.add(value)
        else:
            if prop not in summary:
                summary[prop] = []
            summary[prop].append(value)

    print("Categories: ")
    print(categories)
    print("\nSummary: ")
    print(summary)


def get_property_statistics_wikidata(property_id):
    """
    Retrieves statistics about the distribution of values for a given property in Wikidata.
    """
    # Construct the SPARQL query to retrieve the property values
    query = """
    SELECT ?value WHERE {
        ?item wdt:%s ?value .
        FILTER(isLiteral(?value))
    }
    """ % property_id
    
    # Send the query to the Wikidata SPARQL endpoint
    response = requests.get('https://query.wikidata.org/sparql', params={'query': query, 'format': 'json'})
    
    # Parse the JSON response and extract the property values
    values = [float(result['value']['value']) for result in response.json()['results']['bindings']]
    
    # Calculate the statistics of the property values
    num_values = len(values)
    mean = sum(values) / num_values
    variance = sum((x - mean) ** 2 for x in values) / num_values
    stddev = variance ** 0.5
    min_value = min(values)
    max_value = max(values)
    mode = max(set(values), key = values.count)
    
    # Return the statistics as a dictionary
    return {
        'num_values': num_values,
        'mean': mean,
        'variance': variance,
        'stddev': stddev,
        'min_value': min_value,
        'max_value': max_value,
        'mode': mode
    }

def get_property_statistics_graph(graph, property_id):
    """
    Retrieves statistics about the distribution of values for a given property in a NetworkX graph.
    """
    # Extract the property values from the graph edges
    values = []
    for source, target, data in graph.edges(data=True):
        if data[1] == property_id and isinstance(data[2], (int, float)):
            values.append(data['value'])
    
    # Calculate the statistics of the property values
    num_values = len(values)
    mean = np.mean(values)
    variance = np.var(values)
    stddev = np.std(values)
    min_value = np.min(values)
    max_value = np.max(values)
    mode = float(np.bincount(values).argmax())
    
    # Return the statistics as a dictionary
    return {
        'num_values': num_values,
        'mean': mean,
        'variance': variance,
        'stddev': stddev,
        'min_value': min_value,
        'max_value': max_value,
        'mode': mode
    }

def get_related_properties(property_id):
    """
    Retrieves a list of properties that are related to a given property in Wikidata.
    """
    # Define the SPARQL query to retrieve related properties
    query = """
    SELECT ?relatedProperty ?relatedPropertyName WHERE {
        wd:""" + property_id + """ ?relatedProperty ?relatedPropertyValue .
        ?relatedProperty wikibase:directClaim ?relatedPropertyName .
        FILTER (REGEX(STR(?relatedProperty), "^http://www.wikidata.org/prop/direct"))
    }
    """
    
    # Send the SPARQL query to Wikidata
    url = 'https://query.wikidata.org/sparql'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, params={'format': 'json', 'query': query})
    
    # Parse the response and extract the related properties
    related_properties = []
    for item in response.json()['results']['bindings']:
        property_id = item['relatedProperty']['value'].split('/')[-1]
        property_name = item['relatedPropertyName']['value']
        related_properties.append((property_id, property_name))
    
    # Return the related properties as a list of tuples (property_id, property_name)
    return related_properties

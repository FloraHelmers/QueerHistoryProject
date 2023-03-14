import networkx as nx

from star_merging import star_merging_pipeline
from stats import get_incoming_properties

wikidata_db_ids=["Q328","Q169514","Q8447","Q48183","Q8449","Q206855","Q54919","Q19938912","Q14005","Q648625","Q23833686","Q36578","Q13550863","Q30049687","Q15706812"
                 "Q29861311","Q237227","Q63056","Q504063"] 
#wikipedias,VIAF,BnF,MusicBrainz,Google KG,German National Library,Gemeinsame Normdatei,Czech National Database,BlackPast.org,filmportal.de,SNAC,Brockhaus Enzyklopädie,Find a Grave
#Discogs

trivial_ids=["Q199","Q1985727","Q5","Q6581097","Q1860","Q11573","Q11570","Q6581072"]
#1,calendar,human,male,English?,metre,kilogram,female

timeout_ids=["Q30","Q183"]
#USA,Germany

def explore_selected(dict_properties, n_incr, policy):
    # Concatenate the properties and values in a string to be used in the SPARQL query
    prop_concat=""
    for value,prop in dict_properties.items():
      #prop_concat+="?person "+prop+" wd:"+value+".\n" this part was designed to be able to withstand the big ids of the time_out array
      #by recovering the property first, but the conversion does not work well from rdflib to networkx for this purpose
      prop_concat+="?person ?prop wd:"+value+".\n"
    
    # Create the SPARQL query (maybe use string formatting to make those simpler)
    query='''SELECT DISTINCT ?person ?personLabel 
    WHERE {
    {
        ?person wdt:P31 wd:Q5 . #?personId is a human 
        '''+prop_concat+'''
    
        { 
            ?person wdt:P21 ?sexorgender. #?person has ?sexorgender
            #?sexorgender is not male, female, cisgender male, cigender female, or cisgender person
            FILTER(?sexorgender NOT IN (wd:Q6581097, wd:Q6581072, wd:Q15145778, wd:Q15145779, wd:Q1093205)). 
        } UNION {
            ?person wdt:P91 ?sexualorientation . #?person has ?sexualorientation
            FILTER(?sexualorientation != wd:Q1035954). #?sexualorientation is not heterosexual
        }
    }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE]". }

    } LIMIT '''
    
    # Call the 'star_merging_pipeline' function to extract the people with the selected properties
    return star_merging_pipeline(n_incr, query, policy)

def create_list_prop(list_prop, explored_prop, k_prop):
    to_expl = []  # Create an empty list to store properties to explore
    k = 0  # Counter for how many properties have been added to to_expl
    i = 0  # Counter for the index of properties in list_prop
    
    # Keep looping until k_prop properties have been added to to_expl
    while k < k_prop:
        
        # If the current property has not been explored, add it to to_expl
        if list_prop[i].split('/')[-1] not in explored_prop:
            to_expl.append(list_prop[i])
            k += 1  # Increase the counter for properties added to to_expl
            
        i += 1  # Move on to the next property in list_prop
        
    return to_expl  # Return the list of properties to explore next

def crawler_process(G, n_iter, k_prop, n_incr, policy, n_max=None, people_list=[], alpha=0.85, pagerank_iter=100):
    """
    A function that crawls Wikidata for information about people based on their properties.

    Args:
        G (networkx graph): the starting graph
        n_iter (int): the number of iterations to run the crawler for
        k_prop (int): the number of properties to explore at each iteration
        n_incr (int): the number of new people to query Wikidata for each time a property is explored
        policy (str): the policy to use when querying Wikidata for new people (either "wd" or "spdq")
        n_max (int): the maximum number of people to crawl for
        people_list (list): the list of people already found
        alpha (float): the damping factor to use when computing PageRank
        pagerank_iter (int): the number of iterations to use when computing PageRank

    Returns:
        G (networkx graph): the final graph
        people_list (list): the list of people found during the crawling process
    """

    # Initialize the list of explored properties with pre-defined IDs
    explored_prop=trivial_ids+wikidata_db_ids+timeout_ids
    
    # Loop through a fixed number of iterations
    for i in range(n_iter):
        
        # Compute the PageRank for each node in the graph
        pr = nx.pagerank(G, alpha=alpha, max_iter=pagerank_iter)

        # Extract the top nodes by sorting the PageRank values in decreasing order
        #sorted_nodes = [key.split('/')[-1] for key,val in sorted(pr.items(),key=lambda ele:ele[1],reverse=True) if "entity/" in key]
        sorted_nodes = [key for key, val in sorted(pr.items(), key=lambda ele: ele[1], reverse=True) if "entity/" in key]

        # Create a dictionary of values and their properties to explore next
        to_expl=create_list_prop(sorted_nodes,explored_prop,k_prop)
        print(to_expl)
        #dict_to_expl={prop.split('/')[-1]:get_incoming_properties(G,prop)[0] for prop in to_expl} as seen in the explore_selected function, this part
        #was designed to send the property associated with the entity value to speed up the queries
        dict_to_expl={prop.split('/')[-1]:0 for prop in to_expl}
        
        # Call the 'explore_selected' function to query Wikidata for people with the selected properties
        prop_graph,new_list=explore_selected(dict_to_expl,n_incr,policy)
        
        # Add the newly explored properties to the list of explored properties
        explored_prop+=[prop.split('/')[-1] for prop in to_expl]
        
        # Add the new people found to the list of people
        people_list=list(set(people_list + new_list))
        
        # Add the new nodes and edges to the graph
        G=nx.compose(G,prop_graph)
        
        # Check if the maximum number of people has been reached
        if n_max!=None and len(people_list)>n_max:
            print(str(n_max)+" peoples reached")
            return G, people_list
        
    # Return the final graph and list of people
    return G, people_list
import networkx as nx

import rdflib
from rdflib import Graph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

from utils import get_list_from_sparql,create_merged_stars_graph

def explore_selected(prop,n_incr,endpoint):
    query='''SELECT DISTINCT ?person ?personLabel 
    WHERE {
    {
        ?person wdt:P31 wd:Q5 . #?personId is a human
        ?person ?property wd:'''+prop.split('/')[-1]+'''.
    
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

    data=get_list_from_sparql(endpoint, query, size=n_incr)
    return create_merged_stars_graph(data)

def crawler_process(G, n_iter : int, alpha : float, pagerank_iter : int, k_prop, n_incr, endpoint):
    for i in range(n_iter):
        pr = nx.pagerank(G, alpha=alpha, max_iter=pagerank_iter)

        sorted_nodes = {key:val for key,val in sorted(pr.items(),key=lambda ele:ele[1],reverse=True) if "entity/" in key}
        i=0
        while i<k_prop:
            #should add an if to check if prop one of the type of useful properties (not number or wikipedia etc)
            prop_graph=explore_selected(sorted_nodes[i],n_incr,endpoint)
            G=nx.compose(G,prop_graph)
            i+=1
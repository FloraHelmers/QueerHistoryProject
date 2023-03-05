import networkx as nx

import rdflib
from rdflib import Graph

from utils import star_merging_pipeline

wikidata_db_ids=["Q328","Q169514","Q8447","Q48183","Q8449","Q206855","Q54919","Q19938912","Q14005","Q648625","Q23833686","Q36578","Q13550863","Q30049687","Q15706812"
                 "Q29861311","Q237227","Q63056","Q504063"] 
#wikipedias,VIAF,BnF,MusicBrainz,Google KG,German National Library,Gemeinsame Normdatei,Czech National Database,BlackPast.org,filmportal.de,SNAC,Brockhaus Enzyklopädie,Find a Grave
#Discogs

trivial_ids=["Q199","Q1985727","Q5","Q6581097","Q1860","Q11573","Q11570","Q6581072"]
#1,calendar,human,male,English?,metre,kilogram,female

timeout_ids=["Q30","Q183"]
#USA,Germany
#should add a way to recover the property linking people to these entities (less searching for SPARQL)

def explore_selected(properties,n_incr,policy):
    prop_concat=""
    for p in properties:
      prop_concat+="?person ?property wd:"+p+".\n"
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
    #print(query)
    return star_merging_pipeline(n_incr, query, policy)

def create_list_prop(list_prop,explored_prop,k_prop):
    to_expl=[]
    k=0
    i=0
    while k<k_prop:
      if list_prop[i] not in explored_prop:
        to_expl.append(list_prop[i])
        k+=1
      i+=1
    print(i)
    return to_expl

def crawler_process(G, n_iter, k_prop, n_incr, policy, n_max=None, people_list=[], alpha=0.85, pagerank_iter=100):
    explored_prop=trivial_ids+wikidata_db_ids+timeout_ids
    for i in range(n_iter):
        pr = nx.pagerank(G, alpha=alpha, max_iter=pagerank_iter)

        sorted_nodes = [key.split('/')[-1] for key,val in sorted(pr.items(),key=lambda ele:ele[1],reverse=True) if "entity/" in key]

        to_expl=create_list_prop(sorted_nodes,explored_prop,k_prop)
        print(to_expl)
        #should add an if to check if prop one of the type of useful properties (not number or wikipedia etc)
        prop_graph,new_list=explore_selected(to_expl,n_incr,policy)
        explored_prop+=to_expl
        people_list=list(set(people_list + new_list))
        G=nx.compose(G,prop_graph)
        if n_max!=None and len(people_list)>n_max:
            print(str(n_max)+" peoples reached")
            return G, people_list
    return G, people_list
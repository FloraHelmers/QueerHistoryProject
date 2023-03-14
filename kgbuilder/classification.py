import requests
import json
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
import networkx as nx

def is_wikidata(iri):
    caract = "http://www.wikidata.org/"
    taille = len(caract)
    return iri[:taille] == caract


def is_person(iri):
    """from the wikipedia code returns whether the entity is a person or not"""
    ask_query = "ASK {<"+ iri +"> wdt:P31 wd:Q5.}"
    endpoint_url = "https://query.wikidata.org/sparql"
    headers = {'User-Agent': 'MyBot'}
    payload = {
            'query': ask_query,
            'format': 'json'
        }
    try :
      r = requests.get(endpoint_url, params=payload, headers=headers, timeout=5)
      return r.json()['boolean']
    except  requests.exceptions.Timeout:
      print("the request timed out")
      return None
    

def is_instanceof_subclass(wiki_code_data, wiki_code_class):
    ask_query = "ASK {<"+ wiki_code_data +"> p:P31 ?statement0. ?statement0 (ps:P31/(wdt:P279*)) "+ wiki_code_class +".}"
    endpoint_url = "https://query.wikidata.org/sparql"
    headers = {'User-Agent': 'MyBot'}
    payload = {
            'query': ask_query,
            'format': 'json'
        }
    try :
      r = requests.get(endpoint_url, params=payload, headers=headers, timeout=5)
      return r.json()['boolean']
    except  requests.exceptions.Timeout:
      print("the request timed out")
      return None

def is_geographic_entity(wiki_code_data, with_wd=False):
    if with_wd:
        code = wiki_code_data
    else : code = "wd:"+wiki_code_data
    return is_instanceof_subclass(code, "wd:Q27096213")

def is_temporal_entity(wiki_code_data, with_wd=False):
    if with_wd:
        code = wiki_code_data
    else : code = "wd:"+wiki_code_data
    return is_instanceof_subclass(code, "wd:Q26907166")

def is_group_of_human(wiki_code_data, with_wd=False):
    if with_wd:
        code = wiki_code_data
    else : code = "wd:"+wiki_code_data
    return is_instanceof_subclass(code, "wd:Q16334295")


class_value_to_type = ["not wikidata", "person", "geographic entity", "temporal entity", "group of humans", "other"]
def get_type_from_value(n):
    return class_value_to_type[n]

def get_type_from_iri(iri):
  value = 0       
  #get the wikicode
  if not is_wikidata(iri):
     return "not wikidata"
  for num, funct in enumerate([is_person, is_geographic_entity, is_temporal_entity, is_group_of_human]):
      res = funct(iri, True)
      if not(res is None) and res:
          value = num + 1
          break
  return class_value_to_type[value]


## Get the labels 
def from_node_get_name(iri):
  query = """SElECT ?item ?itemLabel  WHERE{
  BIND(<""" + iri +"""> as ?item).
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  } """
  endpoint_url = "https://query.wikidata.org/sparql"
  headers = {'User-Agent': 'MyBot'}
  payload = {
          'query': query,
          'format': 'json'
      }
  try :
    r = requests.get(endpoint_url, params=payload, headers=headers, timeout=5)
    return r.json()["results"]["bindings"][0]["itemLabel"]['value']
  except  requests.exceptions.Timeout:
    print("the request timed out")
    return None
def conditioned_from_node_get_name(iri):
  if is_wikidata(iri):
    return from_node_get_name(iri)
  else : return None


def create_nodes_DataFrame(nodes, G, degreeG=True, degreeSubG=True, rdf_type=True, labels=True, entity_type=True):
    df = pd.DataFrame(data=nodes, columns=["nodes"])
    if degreeG:
       df["degrees"] = df["nodes"].apply(lambda x: G.degree(x))
    if degreeSubG:
       subG = G.subgraph(nodes)
       df["degreesSub"] = df["nodes"].apply(lambda x: subG.degree(x))
    if rdf_type:
       df["rdf_type"] = df["nodes"].apply(lambda x : type(x))
    if labels:
       df["labels"] = df["nodes"].apply(conditioned_from_node_get_name)
    if entity_type:
       df["entity type"] = df["nodes"].apply(get_type_from_iri)
    print(df.info())
    return df 


def create_subgraph(df_nodes, G, to_keep="to_keep"):
   return G.subgraph(df_nodes.loc[df_nodes[to_keep == True]])

def zoomed_in_graph(df_nodes, G):
  labels = dict({row["node"] : row["itemLabel"] for index, row in df_nodes.iterrows()})
  color_lookup = dict({row["node"] : row["data_type"] for index, row in df_nodes.iterrows()})
  subG = create_subgraph(df_nodes, G)
  pos = nx.spring_layout(subG)
  low, *_, high = sorted(color_lookup.values())
  norm = mpl.colors.Normalize(vmin=low, vmax=high, clip=True)
  mapper = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.coolwarm)

  mpl.rcParams['figure.figsize'] = 12, 7

  nx.draw(subG, 
          nodelist=color_lookup,
          node_size=1000,
          pos = pos,
          node_color=[mapper.to_rgba(i) 
                      for i in color_lookup.values()], 
          with_labels=False)
  nx.draw_networkx_labels(subG, font_color='g', pos= pos, labels=labels)
  plt.show()
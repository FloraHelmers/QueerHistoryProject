# Strategies for creating knowledge graphs to depict a multi-perspective Queer communities representation
by Louann Coste, Flora Helmers, Léo Le Nestour, Mahsa Niazi

# The project
The process is described in the article. 

# the directory kgbuilder
to use like a python library
The notebook ... explains how to use it. 

# Collecting data with SPARQL requests
the file `some_sparql_requests` proposes several sparql requests.
The .csv files that come along are the results of some of these sparql requests.  

# writing ontology
Finally not exploited as a part of the project. The ontology created offers a view of the LGBTQ+ artistic and politic scene. Its serialization format in turtle is easily readable. 
The ontology can be visualize by using Protégé. 

# In the directory visualisation 
several visualisation are gathered



# Technical reminders
To run kgbuilder in google colab : 
1. upload kgbuiler in the google drive
2. run : ```python
    from google.colab import drive
    drive.mount("/content/gdrive")
    sys.path.append('/content/gdrive/MyDrive/{the access path to kgbuilder}/kgbuilder')```

# Strategies for creating knowledge graphs to depict a multi-perspective Queer communities representation
by Louann Coste, Flora Helmers, Léo Le Nestour, Mahsa Niazi

## Project Overview
This project aims to create a knowledge graph of the LGBTQ+ artistic and political scene. The process and details are explained in the accompanying article.

## KGBuilder Directory
The KGBuilder directory can be used as a Python library, and the accompanying notebook (present both inside and outside the directory) provides a step-by-step guide on how to use it.

## Data Collection with SPARQL Requests
The "some_sparql_requests" file contains several SPARQL requests to collect data. The results of some of these requests are stored in CSV files.

## Ontology Writing
An ontology was created to offer a view of the LGBTQ+ artistic and political scene, but it was not exploited as part of the project. The ontology is serialized in turtle format, which is easily readable. It can be visualized using Protégé.

## Visualization Directory
The Visualization directory contains several visualizations of the knowledge graph.

## Bibliography
The Bibliography section lists the sources we consulted to gain more knowledge about knowledge graphs.

## Additional Notebooks
Additional notebooks are provided, but they are raw and not necessary to read.

## Technical details if you want to run the library in Colab
To run kgbuilder in google colab : 
1. upload kgbuiler in the google drive
2. run : ```python
    from google.colab import drive
    drive.mount("/content/gdrive")
    sys.path.append('/content/gdrive/MyDrive/{the access path to kgbuilder}/kgbuilder')```

Otherwise, it is sufficient to have the path of the library in sys paths.

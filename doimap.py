import requests
import networkx as nx
import bibtexparser
import os.path

bib_filename = 'my_bibliography.bib'

if not os.path.isfile(bib_filename):
    print(f"Error: could not find file '{bib_filename}'")
else:
    with open(bib_filename, encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
                
        # Extract DOIs from entries in bib_database
        doi_list = []
        for entry in bib_database.entries:
            if 'doi' in entry:
                doi_list.append(entry['doi'])


        # Initialize empty directed graph
        G = nx.DiGraph()

        # Loop over DOIs
        for doi in doi_list:
            # Construct URL to retrieve citation data
            url = f"https://api.crossref.org/works/{doi}"

            # Retrieve article metadata
            response = requests.get(url)

            # Extract article title
            title = ""
            if response.status_code == 200:
                data = response.json()
                if "title" in data["message"]:
                    title = data["message"]["title"][0]

            # Add node to graph with title as node attribute
            G.add_node(doi, title=title)

            # Retrieve citation data
            response = requests.get(url)

            # Extract DOIs of cited articles that are in doi_list
            cited_dois = []
            if response.status_code == 200:
                data = response.json()
                if "reference" in data["message"]:
                    for item in data["message"]["reference"]:
                        if "DOI" in item:
                            cited_doi = item["DOI"]
                            if cited_doi in doi_list:
                                cited_dois.append(cited_doi)

            # Add edges to graph
            for cited_doi in cited_dois:
                G.add_edge(doi, cited_doi)

        # Set node labels to article titles
        node_labels = nx.get_node_attributes(G, "title")
        for doi, title in node_labels.items():
            if len(title) > 30:
                node_labels[doi] = title[:27] + '...'

        nx.draw(G, with_labels=True, labels=node_labels)

        # Show plot
        import matplotlib.pyplot as plt
        plt.show()

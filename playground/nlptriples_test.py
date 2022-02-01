from nlptriples import triples


if __name__ == "__main__":

    rdf = triples.RDF_triple()
    triple = rdf.extract(sent)
    print(triple)
from wikipedia_shexer.core.wikipedia_triple_extractor import WikipediaTripleExtractor
from sklearn import svm

triples_file = "generated.ttl"
rows_file = r"F:\datasets\300from200_row_features.csv"
typing_file = r"F:\datasets\300from200_some_types.nt"
ontology_file = r"F:\datasets\dbpedia_2021_07.owl"
wikilinks_file = r"F:\datasets\300from200_some_links.nt"

t_ext = WikipediaTripleExtractor(typing_file=typing_file,
                                 wikilinks_file=wikilinks_file,
                                 ontology_file=ontology_file)

t_ext.extract_triples_of_rows(rows_file=rows_file,
                              triples_out_file=triples_file,
                              training_data_file=rows_file,
                              callback=svm.SVC,
                              include_typing_triples=True)

print("Done!")
from wikipedia_shexer.core.wikipedia_triple_extractor import WikipediaTripleExtractor
from sklearn import svm

triples_file = "generated.ttl"
rows_file = r"F:\datasets\300from200_row_features.csv"

t_ext = WikipediaTripleExtractor(typing_file=None,
                                 wikilinks_file=None,
                                 ontology_file=None)

t_ext.extract_triples_of_rows(rows_file=rows_file,
                              triples_out_file=triples_file,
                              training_data_file=rows_file,
                              callback=svm.SVC)

print("Done!")
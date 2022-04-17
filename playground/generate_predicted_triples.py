from wikipedia_shexer.core.wikipedia_triple_extractor import WikipediaTripleExtractor
from sklearn import svm

triples_file = r"F:\datasets\some_bands_triples.ttl"
rows_file = r"F:\datasets\300from200_row_features_no_heads.csv"
titles_file = r"F:\datasets\some_band_names.csv"
new_rows_file = r"F:\datasets\some_bands_candidate_features.csv"
# typing_file = r"F:\datasets\instance-types_lang=en_specific.ttl"
typing_file = r"F:\datasets\300from200_some_types.nt"
ontology_file = r"F:\datasets\dbpedia_2021_07.owl"
wikilinks_file = r"F:\datasets\300from200_some_links.nt"

t_ext = WikipediaTripleExtractor(typing_file=typing_file,
                                 wikilinks_file=wikilinks_file,
                                 ontology_file=ontology_file)

# t_ext.extract_triples_of_titles_file(titles_file=titles_file,
#                                      rows_out_file=new_rows_file,
#                                      triples_out_file=triples_file,
#                                      training_data_file=training_rows_file,
#                                      callback=svm.SVC,
#                                      include_typing_triples=True)

t_ext.extract_triples_of_rows(rows_file=new_rows_file,
                              triples_out_file=triples_file,
                              training_data_file=rows_file,
                              callback=svm.SVC,
                              include_typing_triples=True)

# t_ext.extract_triples_of_rows(training_rows_file=training_rows_file,
#                               triples_out_file=triples_file,
#                               training_data_file=training_rows_file,
#                               callback=svm.SVC,
#                               include_typing_triples=True)

print("Done!")
from wikipedia_shexer.core.wikipedia_shape_extractor import WikipediaShapeExtractor
from sklearn import svm

# triples_file = r"F:\datasets\300from200_triples_with_model.ttl"
# training_rows_file = r"F:\datasets\300from200_row_features.csv"
# typing_file = r"F:\datasets\instance-types_lang=en_specific.ttl"
# ontology_file = r"F:\datasets\dbpedia_2021_07.owl"
# wikilinks_file = r"F:\datasets\300from200_some_links.nt"
# out_shapes_file = r"F:\datasets\300from200_shapes.nt"

triples_file = r"F:\datasets\some_bands_triples.ttl"
training_rows_file = r"F:\datasets\300from200_row_features.csv"
titles_file = r"F:\datasets\some_band_names.csv"
new_rows_file = r"F:\datasets\some_bands_candidate_features.csv"
typing_file = r"F:\datasets\instance-types_lang=en_specific.ttl"
# typing_file = r"F:\datasets\300from200_some_types.nt"
ontology_file = r"F:\datasets\dbpedia_2021_07.owl"
# wikilinks_file = r"F:\datasets\300from200_some_links.nt"
wikilinks_file = r"F:\datasets\wikilinks_lang=en.ttl"
out_shapes_file = r"F:\datasets\some_bands_shapes.shex"

print("ini!")
t_sha = WikipediaShapeExtractor(typing_file=typing_file,
                                wikilinks_file=wikilinks_file,
                                ontology_file=ontology_file,
                                all_classes_mode=True)
print("Built stuff!")
# t_sha.extract_shapes_of_rows(training_rows_file=training_rows_file,
#                              triples_out_file=triples_file,
#                              training_data_file=training_rows_file,
#                              callback=svm.SVC,
#                              include_typing_triples=True,
#                              shapes_out_file=out_shapes_file)
t_sha.extract_shapes_of_titles_file(titles_file=titles_file,
                                    include_typing_triples=True,
                                    triples_out_file=triples_file,
                                    shapes_out_file=out_shapes_file,
                                    callback=svm.SVC,
                                    training_data_file=training_rows_file,
                                    rows_out_file=new_rows_file)

print("Done!")

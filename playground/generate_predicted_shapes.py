from wikipedia_shexer.core.wikipedia_shape_extractor import WikipediaShapeExtractor
from sklearn import svm

triples_file = r"F:\datasets\300from200_triples_with_model.ttl"
rows_file = r"F:\datasets\300from200_row_features.csv"
typing_file = r"F:\datasets\instance-types_lang=en_specific.ttl"
ontology_file = r"F:\datasets\dbpedia_2021_07.owl"
wikilinks_file = r"F:\datasets\300from200_some_links.nt"
out_shapes_file = r"F:\datasets\300from200_shapes.nt"

print("ini!")
t_sha = WikipediaShapeExtractor(typing_file=typing_file,
                                wikilinks_file=wikilinks_file,
                                ontology_file=ontology_file,
                                all_classes_mode=True)
print("Built stuff!")
t_sha.extract_shapes_of_rows(rows_file=rows_file,
                             triples_out_file=triples_file,
                             training_data_file=rows_file,
                             callback=svm.SVC,
                             include_typing_triples=True,
                             shapes_out_file=out_shapes_file)

print("Done!")

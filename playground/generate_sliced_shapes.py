from wikipedia_shexer.core.wikipedia_shape_extractor import WikipediaShapeExtractor
from sklearn import svm


# triples_file = r"F:\datasets\every_triple_attempt.ttl"  # out triples
triples_file = r"/ws_app/300from200_not_sliced_every_triple.ttl"  # out triples

# training_rows_file = r"F:\datasets\300from200_row_features.csv" # training data
training_rows_file = r"/ws_app/300from200_row_features.csv" # training data

# titles_file = r"F:\datasets\300from200_every_instance.csv" #target_files
titles_file = r"/ws_app/300from200_every_instance.csv" #target_files

# new_rows_file = r"F:\datasets\300from200_candidate_features.csv" #candidate rows
new_rows_file = r"/ws_app/300from200_all_candidate_features.csv" #candidate rows

# typing_file = r"F:\datasets\instance-types_lang=en_specific.ttl" #typing file
typing_file = r"/ws_app/instance-types_lang=en_specific.ttl" #typing file

# ontology_file = r"F:\datasets\dbpedia_2021_07.owl" # ontology file
ontology_file = r"/ws_app/dbpedia_2021_07.owl" # ontology file

# wikilinks_file = r"F:\datasets\some_wikilinks.ttl"  # wikilinks file
wikilinks_file = r"/ws_app/wikilinks_lang=en.ttl"  # wikilinks file

# out_shapes_file = r"F:\datasets\every_shape_attempt.shex"  # out shapes
out_shapes_file = r"/ws_app/300from200_nor_sliced_every_shape.shex"  # out shapes

# wikipedia_dump_file = r"F:\datasets\enwiki-20210501-pages-articles-multistream.xml" \
#                       r"\enwiki-20210501-pages-articles-multistream.xml"
wikipedia_dump_file = r"/ws_app/enwiki-20210501-pages-articles-multistream.xml"

print("ini!")
t_sha = WikipediaShapeExtractor(typing_file=typing_file,
                                wikilinks_file=wikilinks_file,
                                ontology_file=ontology_file,
                                all_classes_mode=True)
print("Built stuff!")

t_sha.extract_shapes_of_titles_file(titles_file=titles_file,
                                    include_typing_triples=True,
                                    triples_out_file=triples_file,
                                    shapes_out_file=out_shapes_file,
                                    callback=svm.SVC,
                                    training_data_file=training_rows_file,
                                    rows_out_file=new_rows_file,
                                    wikipedia_dump_file=wikipedia_dump_file)

print("Done!")

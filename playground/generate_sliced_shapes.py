# from wikipedia_shexer.core.wikipedia_shape_extractor import WikipediaShapeExtractor
# from sklearn import svm


# triples_file = r"F:\datasets\every_triple_attempt.ttl"  # out triples
# triples_file = r"/ws_app/300from200_not_sliced_every_triple.ttl"  # out triples

# training_rows_file = r"F:\datasets\300from200_row_features.csv" # training data
# training_rows_file = r"/ws_app/300from200_row_features.csv" # training data

# titles_file = r"F:\datasets\300from200_every_instance.csv" #target_files
# titles_file = r"/ws_app/300from200_every_instance.csv" #target_files

# new_rows_file = r"F:\datasets\300from200_candidate_features.csv" #candidate rows
# new_rows_file = r"/ws_app/300from200_all_candidate_features.csv" #candidate rows

# typing_file = r"F:\datasets\instance-types_lang=en_specific.ttl" #typing file
# typing_file = r"/ws_app/instance-types_lang_en_transitive.ttl" #typing file
#
# # ontology_file = r"F:\datasets\dbpedia_2021_07.owl" # ontology file
# ontology_file = r"/ws_app/dbpedia_2021_07.owl" # ontology file

# wikilinks_file = r"F:\datasets\some_wikilinks.ttl"  # wikilinks file
# wikilinks_file = r"/ws_app/wikilinks_lang_en.ttl"  # wikilinks file

# out_shapes_file = r"F:\datasets\every_shape_attempt.shex"  # out shapes
# out_shapes_file = r"/ws_app/300from200_not_sliced_every_shape.shex"  # out shapes

# wikipedia_dump_file = r"F:\datasets\enwiki-20210501-pages-articles-multistream.xml" \
#                       r"\enwiki-20210501-pages-articles-multistream.xml"


# wikipedia_dump_file = r"/ws_app/enwiki-20210501-pages-articles-multistream.xml"

# print("ini!")
# t_sha = WikipediaShapeExtractor(typing_file=typing_file,
#                                 wikilinks_file="noneed",
#                                 ontology_file=ontology_file,
#                                 all_classes_mode=True)
# print("Built stuff!")
# t_sha.extract_shapes_of_titles_file(titles_file=titles_file,
#                                     include_typing_triples=True,
#                                     triples_out_file=triples_file,
#                                     shapes_out_file=out_shapes_file,
#                                     callback=svm.SVC,
#                                     training_data_file=training_rows_file,
#                                     rows_out_file=new_rows_file,
#                                     wikipedia_dump_file=wikipedia_dump_file)
#
# t_sha.extract_shapes_of_rows(rows_file=candidate_rows_file,
#                              callback=svm.SVC,
#                              training_data_file="",
#                              include_typing_triples=True,
#                              shape_threshold=0.05,
#                              triples_out_file="",
#                              shapes_out_file="")

from wikipedia_shexer.core.wikipedia_shape_extractor import WikipediaShapeExtractor
from sklearn import svm
import json

CLASS_POSITION_IC_FILE = 0
NUMBER_OF_FIELDS = 14
INSTANCE_POSITION = 1
MIN_LINES = 150
MIN_INSTANCES = 30

def load_target_classes_list(i_c_file):
    result = []
    with open(i_c_file, "r", encoding="utf-8") as in_stream:
        json_obj = json.load(in_stream)
        for a_class_list in json_obj:
            result.append(a_class_list[CLASS_POSITION_IC_FILE].replace("http://dbpedia.org/ontology/",""))
    return result

def has_minimum_size(target_file: str) -> bool:
    instances = set()
    try:
        with open(target_file, "r", encoding="utf-8") as in_stream:
            counter = 0
            for a_line in  in_stream:
                pieces = a_line.strip().split(";")
                if len(pieces) == NUMBER_OF_FIELDS:
                    counter += 1
                    instances.add(pieces[INSTANCE_POSITION])
                    if counter >= MIN_LINES and len(instances) >= MIN_INSTANCES:
                        return True
    except FileNotFoundError:
        return False
    return False


def run(i_c_file,
        candidate_features_pattern_file,
        shape_out_pattern_file,
        typing_file, ontology_file,
        training_pattern_file,
        triples_out_pattern_file):
    print("Starting process...")
    t_sha = WikipediaShapeExtractor(typing_file=typing_file,
                                    wikilinks_file="noneed",
                                    ontology_file=ontology_file,
                                    all_classes_mode=True)
    print("Structures built, typing cache should be ready")
    target_classes = load_target_classes_list(i_c_file)
    for a_class in target_classes:
        training_features_file = training_pattern_file.format(a_class)
        if has_minimum_size(training_features_file):
            print("CLASS     {}    ---------------".format(a_class))
            t_sha.extract_shapes_of_rows(rows_file=candidate_features_pattern_file.format(a_class),
                                         callback=svm.SVC,
                                         training_data_file=training_features_file,
                                         include_typing_triples=False,
                                         shape_threshold=0.02,
                                         triples_out_file=triples_out_pattern_file.format(a_class),
                                         shapes_out_file=shape_out_pattern_file.format(a_class))
        else:
            print("Class discarded: {}. Not enough data in training rows.".format(a_class))

if __name__ == "__main__":

    run(i_c_file=r"F:\datasets\300instances_from_200classes.json",
        candidate_features_pattern_file=r"F:\datasets\sliced_features\{}_candidate_features.csv",
        shape_out_pattern_file=r"F:\datasets\sliced_shapes\{}_candidate_shapes.shex",
        typing_file=r"F:\datasets\instance-types_lang=en_specific.ttl",
        ontology_file=r"F:\datasets\dbpedia_2021_07.owl",
        training_pattern_file=r"F:\datasets\training_rows_per_class\{}_row_reatures.csv",
        triples_out_pattern_file=r"F:\datasets\sliced_triples\{}_candidate_triples.ttl")
    print("Done!")

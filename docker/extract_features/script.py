from configparser import ConfigParser
import sys
from time import time
from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import dbpedia_id_to_page_title
from wikipedia_shexer.utils.cache import DestFilteredBackLinkCache
from wikipedia_shexer.model.ontology import Ontology
from wikipedia_shexer.utils.cache import DestFilteredTypingCache
from wikipedia_shexer.core.wikipedia_dump_extractor import WikipediaDumpExtractor
from wikipedia_shexer.features.feature_serialization import CSVRowSerializator
from wikipedia_shexer.features.feature_extractor import FeatureExtractor


def read_nodes_list(nodes_path):
    result = set()
    with open(nodes_path, "r") as in_stream:
        for a_line in in_stream:
            a_line = a_line.strip()
            if a_line != "":
                result.add(a_line)

def run(ini_file):

    parser = ConfigParser()
    parser.read(ini_file)

    ontology_path = parser.get("ontology", "ontology_path")
    types_file = parser.get("dbpedia", "types_path")
    wikilinks_file = parser.get("dbpedia", "wikilinks_path")
    wikipedia_dump_file = parser.get("wikipedia", "dump_path")
    dbpedia_dump_files = parser.get("dbpedia", "dump_path").split("|")
    important_nodes_path = parser.get("targets", "nodes_path")
    result_path = parser.get("result", "result_path")

    target_iris = list(read_nodes_list(important_nodes_path))
    target_pages = [dbpedia_id_to_page_title(a_db_id) for a_db_id in target_iris]

    print("Targets done!")

    i = 0
    ini = time()

    i += 1  # 1
    print(i, (time() - ini) / 60, "minutes")

    ontology = Ontology(source_file=ontology_path)

    i += 1  # 2
    print(i, (time() - ini) / 60, "minutes")

    type_cache = DestFilteredTypingCache(source_file=types_file,
                                         target_iris=target_iris,
                                         ontology=ontology,
                                         filter_out_of_dbpedia=True,
                                         discard_superclasses=False,
                                         fill_with_ontology_superclasses=True)

    i += 1  # 3
    print(i, (time() - ini) / 60, "minutes")

    backlink_cache = DestFilteredBackLinkCache(source_file=wikilinks_file,
                                               target_iris=target_iris)

    i += 1  # 4
    print(i, (time() - ini) / 60, "minutes")

    extractor = FeatureExtractor(ontology=ontology,
                                 type_cache=type_cache,
                                 backlink_cache=backlink_cache)

    i += 1  # 5
    print(i, (time() - ini) / 60, "minutes")

    model_extractor = WikipediaDumpExtractor(wikipedia_dump_file=wikipedia_dump_file,
                                             dbpedia_source_files=dbpedia_dump_files)

    i += 1  # 6
    print(i, (time() - ini) / 60, "minutes")

    abstracts = [elem for elem in model_extractor.extract_titles_model(target_pages)]

    i += 1  # 7
    print(i, (time() - ini) / 60, "minutes")

    new_target_nodes = []
    for an_abstract in abstracts:
        for a_mention in an_abstract.mentions():
            new_target_nodes.append(a_mention.dbpedia_id)

    type_cache.expand_target_iris(new_target_nodes)

    i += 1  # 8
    print(i, (time() - ini) / 60, "minutes")

    with open(result_path, "w") as out_str:
        serializator = CSVRowSerializator()
        for an_abstract in abstracts:
            for a_csv_row in serializator.serialize_rows(extractor.rows_from_abstract(an_abstract)):
                out_str.write(a_csv_row + "\n")

    i += 1  # 9
    print(i, (time() - ini) / 60, "minutes")

    # print("Ontology file: {}".format(parser.get("ontology", "ontology_path")))
    # print("Wikipedia dump file: {}".format(parser.get("wikipedia", "dump_path")))
    # print("Important nodes file: {}".format(parser.get("targets", "nodes_path")))
    #
    # print("Dbepdia")
    # print("Types: {}".format(parser.get("dbpedia", "types_path")))
    # print("Wikilinks: {}".format(parser.get("dbpedia", "wikilinks_path")))
    #
    # dbp_dump_files = parser.get("dbpedia", "dump_path").split("|")
    # print("Dump_files: {}".format(", ".join(dbp_dump_files)))
    #
    #
    # print("Results will be outputed to: {}".format(parser.get("result", "result_path")))


if __name__ == "__main__":
    print("Input location: {}".format(sys.argv[1]))
    run(sys.argv[1])



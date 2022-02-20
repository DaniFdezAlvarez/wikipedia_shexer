from wikipedia_shexer.core.fred_triple_extractor import FredTripleExtractor
from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import dbpedia_id_to_page_title
from playground.config import API_KEY
import json
from shexer.shaper import Shaper
from shexer.consts import NT
import sys
from datetime import datetime


def f_print(*msgs):
    print(msgs)
    sys.stdout.flush()

def now():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def class_instances_tuples(class_instances_file):
    with open(class_instances_file, "r", encoding="utf-8") as in_stream:
        json_obj = json.load(in_stream)
        for a_class_list in json_obj:
            candidate_class = dbpedia_id_to_page_title(a_class_list[0])
            if len(a_class_list[1]) > 200:
                candidate_instances = [dbpedia_id_to_page_title(elem) for elem in a_class_list[1]]
                yield candidate_class, candidate_instances

def instances_to_file(instances, file_path):
    with open(file_path, "w", encoding="utf-8") as out_stream:
        out_stream.write("\n".join(instances))

def class_file_with_pattern(class_title, file_pattern):
    return file_pattern.format(class_title)


def shex_class(triples_in_file, shapes_out_file, namespaces):
    shaper = Shaper(all_classes_mode=True,
                    graph_file_input=triples_in_file,
                    namespaces_dict=namespaces,
                    input_format=NT)
    shaper.shex_graph(output_file=shapes_out_file)

def compute_class_instances(class_title,
                            instance_titles,
                            extractor,
                            tmp_file,
                            wikipedia_dump_file,
                            triple_file_pattern,
                            shapes_file_pattern,
                            namespaces):
    f_print("----------------------")
    f_print("Computing {} class. It has {} instances.\nStart time: {}".format(class_title, len(instance_titles), now()))
    instances_to_file(instances=instance_titles,
                      file_path=tmp_file)
    triples_file = class_file_with_pattern(class_title=class_title,
                                           file_pattern=triple_file_pattern)
    extractor.reset_count()
    extractor.extract_triples_of_titles_file(titles_file=tmp_file,
                                             triples_out_file=triples_file,
                                             wikipedia_dump_file=wikipedia_dump_file)
    f_print("Triples of {} extracted.\nPetitions performed: {}.\nTime: {} ".format(class_title, extractor.petitions_performed, now()))
    shex_class(triples_in_file=triples_file,
               shapes_out_file=class_file_with_pattern(class_title=class_title,
                                                       file_pattern=shapes_file_pattern),
               namespaces=namespaces)


def run(class_instances_file,
        tmp_file,
        wikipedia_dump_file,
        triple_file_pattern,
        shapes_file_pattern,
        namespaces):

    f_print("Starting execution...")

    extractor = FredTripleExtractor(api_key=API_KEY,
                                    petitions_already_performed=0)

    f_print("Extractor built. Generating class-intances pairs...")

    for a_class, instances in class_instances_tuples(class_instances_file):
        compute_class_instances(class_title=a_class,
                                instance_titles=instances,
                                extractor=extractor,
                                tmp_file=tmp_file,
                                wikipedia_dump_file=wikipedia_dump_file,
                                triple_file_pattern=triple_file_pattern,
                                shapes_file_pattern=shapes_file_pattern,
                                namespaces=namespaces)

if __name__ == "__main__":
    class_instances_file = "/home/danifdz/data/300instances_from_200classes.json"
    tmp_file = "/home/danifdz/data/fred/tmp_title.tsv"
    wikipedia_dump_file = "/home/danifdz/data/enwiki-dump.xml"
    triple_file_pattern = "/home/danifdz/data/fred/triples/{}.nt"
    shapes_file_pattern = "/home/danifdz/data/fred/shapes/{}.shex"
    namespaces = \
        {
            "http://www.w3.org/XML/1998/namespace/": "xml",
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
            "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
            "http://www.w3.org/2001/XMLSchema#": "xsd",
            "http://xmlns.com/foaf/0.1/": "foaf",
            "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#" : "dul",
            "https://w3id.org/framester/schema/" : "framester",
            "http://www.ontologydesignpatterns.org/ont/fred/domain.owl#" : "fred",
            "http://schema.org/" : "schema",
            "http://www.ontologydesignpatterns.org/ont/framenet/abox/fe/" : "fe",
            "http://www.ontologydesignpatterns.org/ont/boxer/boxer.owl#" : "boxer",
            "http://dbpedia.org/resource/" : "dbr",
            "http://dbpedia.org/ontology/": "dbo",
        }
    run(class_instances_file=class_instances_file,
        tmp_file=tmp_file,
        wikipedia_dump_file=wikipedia_dump_file,
        triple_file_pattern=triple_file_pattern,
        shapes_file_pattern=shapes_file_pattern,
        namespaces=namespaces)

    f_print("Done!")





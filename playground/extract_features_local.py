from wikipedia_shexer.io.json_io import read_json_obj_from_path
from time import time
from wikipedia_shexer.features.feature_extractor import FeatureExtractor
from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import dbpedia_id_to_page_title
from wikipedia_shexer.utils.cache import DestFilteredBackLinkCache
from wikipedia_shexer.model.ontology import Ontology
from wikipedia_shexer.utils.cache import DestFilteredTypingCache
from wikipedia_shexer.core.wikipedia_dump_extractor import WikipediaDumpExtractor
from wikipedia_shexer.features.feature_serialization import CSVRowSerializator

ontology_path = r"files\dbpedia_2021_07.owl"
# types_file = r"F:\datasets\instance-types_lang=en_transitive.ttl"
types_file = r"F:\mad\mad_types.ttl"
# wikilinks_file = r"F:\datasets\wikilinks_lang=en.ttl"
wikilinks_file = r"F:\mad\mad_wikilinks.ttl"
# wikipedia_dump_file = r"F:\datasets\enwiki-20210501-pages-articles-multistream.xml\enwiki-20210501-pages-articles-multistream.xml"
wikipedia_dump_file = r"F:\mad\mad_wiki.xml"
# dbpedia_dump_files = [r"F:\datasets\mappingbased-objects.ttl",
#                       r"F:\datasets\infobox-properties_lang=en.ttl"
#                       ]
dbpedia_dump_files = [r"F:\mad\mad_mapping_based.ttl",
                      r"F:\mad\mad_infobox.ttl"
                      ]

# important_nodes_path = r"C:\Users\Dani\Documents\EII\doctorado\PAPERS_PROPIOS\wikipedia_shexer\datasets\300instances_from_200classes.json"
important_nodes_path = r"F:\mad\targets.json"
# result_path = "300from200.csv"
result_path = "mad.csv"

def read_nodes_list(nodes_path):
    result = set()
    target_obj = read_json_obj_from_path(nodes_path)
    for a_list1 in target_obj:
        for elem in a_list1[1]:
            print(elem)
            result.add(elem)
    return result

target_iris = list(read_nodes_list(important_nodes_path))
target_pages = [dbpedia_id_to_page_title(a_db_id) for a_db_id in target_iris]

print("Targets done!")

i = 0
ini = time()

i += 1  # 1
print(i, (time()-ini)/60, "minutes")

ontology = Ontology(source_file=ontology_path)

i += 1  # 2
print(i, (time()-ini)/60, "minutes")

type_cache = DestFilteredTypingCache(source_file=types_file,
                                     target_iris=target_iris,
                                     ontology=ontology,
                                     filter_out_of_dbpedia=True,
                                     discard_superclasses=False,
                                     fill_with_ontology_superclasses=True)

i += 1  # 3
print(i, (time()-ini)/60, "minutes")

backlink_cache = DestFilteredBackLinkCache(source_file=wikilinks_file,
                                           target_iris=target_iris)

i += 1   # 4
print(i, (time()-ini)/60, "minutes")

extractor = FeatureExtractor(ontology=ontology,
                             type_cache=type_cache,
                             backlink_cache=backlink_cache)

i += 1  # 5
print(i, (time()-ini)/60, "minutes")

model_extractor = WikipediaDumpExtractor(wikipedia_dump_file=wikipedia_dump_file,
                                         dbpedia_source_files=dbpedia_dump_files)

i += 1  # 6
print(i, (time()-ini)/60, "minutes")

abstracts = model_extractor.extract_titles_model(target_pages)

i += 1  # 7
print(i, (time()-ini)/60, "minutes")

with open(result_path, "w") as out_str:
    serializator = CSVRowSerializator()
    for an_abstract in abstracts:
        for a_csv_row in serializator.serialize_rows(extractor.rows_from_abstract(an_abstract)):
            print("We,", a_csv_row)
            out_str.write(a_csv_row + "\n")

i += 1  # 8
print(i, (time()-ini)/60, "minutes")

print("Done!")
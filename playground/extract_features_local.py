
from time import time
from wikipedia_shexer.features.feature_extractor import FeatureExtractor
from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import page_id_to_DBpedia_id
from wikipedia_shexer.utils.cache import DestFilteredBackLinkCache
from wikipedia_shexer.model.ontology import Ontology
from wikipedia_shexer.utils.cache import DestFilteredTypingCache
from wikipedia_shexer.core.wikipedia_dump_extractor import WikipediaDumpExtractor

ontology_path = r"files\dbpedia_2014.owl"
types_file = r"F:\datasets\instance-types_lang=en_transitive.ttl"
wikilinks_file = r"F:\datasets\wikilinks_lang=en.ttl"
wikipedia_dump_file = r"F:\datasets\enwiki-20210501-pages-articles-multistream.xml\enwiki-20210501-pages-articles-multistream.xml"
dbpedia_dump_files = [r"F:\datasets\mappingbased-objects.ttl",
                      r"F:\datasets\infobox-properties_lang=en.ttl"
                      ]

target_pages = ["Alaska"]
target_iris = [ page_id_to_DBpedia_id(a_page) for a_page in target_pages]

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
                                     discard_superclasses=True)

i += 1  # 3
print(i, (time()-ini)/60, "minutes")

backlink_cache = DestFilteredBackLinkCache(source_file=types_file,
                                           target_iris=target_iris)

i += 1   # 4
print(i, (time()-ini)/60, "minutes")

extractor = FeatureExtractor(ontology=ontology,
                             type_cache=type_cache,
                             backlink_cache=wikilinks_file)

i += 1  # 5
print(i, (time()-ini)/60, "minutes")

model_extractor = WikipediaDumpExtractor(wikipedia_dump_file=wikipedia_dump_file,
                                         dbpedia_source_files=dbpedia_dump_files)

i += 1  # 6
print(i, (time()-ini)/60, "minutes")

abstracts = model_extractor.extract_titles_model(target_pages)

i += 1  # 7
print(i, (time()-ini)/60, "minutes")

for an_abstract in abstracts:
    rows = extractor.rows_from_abstract(an_abstract)

i += 1  # 8
print(i, (time()-ini)/60, "minutes")

print("Done!")


from wikipedia_shexer.features.feature_extractor import FeatureExtractor
from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import page_id_to_DBpedia_id
from wikipedia_shexer.utils.cache import DestFilteredBackLinkCache
from wikipedia_shexer.model.ontology import Ontology
from wikipedia_shexer.utils.cache import DestFilteredTypingCache

ontology_path = r"files\dbpedia_2014.owl"
types_file = r"F:\datasets\instance-types_lang=en_transitive.ttl"
wikilinks_file = r"F:\datasets\wikilinks_lang=en.ttl"

target_pages = ["Alaska"]
target_iris = [ page_id_to_DBpedia_id(a_page) for a_page in target_pages]

ontology = Ontology(source_file=ontology_path)

type_cache = DestFilteredTypingCache(source_file=types_file,
                                     target_iris=target_iris,
                                     ontology=ontology,
                                     filter_out_of_dbpedia=True,
                                     discard_superclasses=True)

backlink_cache = DestFilteredBackLinkCache(source_file=types_file,
                                           target_iris=target_iris)


extractor = FeatureExtractor(ontology=ontology,
                             type_cache=type_cache,
                             backlink_cache=wikilinks_file)

# TODO CONTINUE HERE, GET THE MODELS

for an_abstract in []:
    rows = extractor.rows_from_abstract(an_abstract)
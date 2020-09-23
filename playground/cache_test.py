from wikipedia_shexer.model.ontology import Ontology
from wikipedia_shexer.utils.cache import TypingCache
target_node = "http://dbpedia.org/resource/Alabama"
ontology = Ontology(source_file="files\\dbpedia_2014.owl")

typing_file = "C:\\Users\\Dani\\Documents\\EII\\doctorado\\papers_propios\\wikipedia_shexer\\instance-types_lang_en_transitive.ttl"

# t_cache = TypingCache(source_file=typing_file,
#                       ontology=ontology,
#                       filter_out_of_dbpedia=False,
#                       discard_superclasses=False)
#
# print(t_cache.get_types_of_node(target_node))
#
# t_cache = TypingCache(source_file=typing_file,
#                       ontology=ontology,
#                       filter_out_of_dbpedia=True,
#                       discard_superclasses=False)
#
# print(t_cache.get_types_of_node(target_node))

t_cache = TypingCache(source_file=typing_file,
                      ontology=ontology,
                      filter_out_of_dbpedia=True,
                      discard_superclasses=True)

print(t_cache.get_types_of_node(target_node))

print("Done!")
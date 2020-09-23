from wikipedia_shexer.model.ontology import Ontology
from wikipedia_shexer.utils.cache import TypingCache, BackLinkCache
# target_node = "http://dbpedia.org/resource/Alabama"
target_node = "http://dbpedia.org/resource/AbacuS"

# ontology = Ontology(source_file="files\\dbpedia_2014.owl")

typing_file = "C:\\Users\\Dani\\Documents\\EII\\doctorado\\papers_propios\\wikipedia_shexer\\instance-types_lang_en_transitive.ttl"
wikilinks_file = "C:\\Users\\Dani\\Documents\\EII\\doctorado\\papers_propios\\wikipedia_shexer\\wikilinks_lang_en.ttl"
# C:\Users\Dani\Documents\EII\doctorado\papers_propios\wikipedia_shexer

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

# t_cache = TypingCache(source_file=typing_file,
#                       ontology=ontology,
#                       filter_out_of_dbpedia=True,
#                       discard_superclasses=True)
#
# print(t_cache.get_types_of_node(target_node))

l_cache = BackLinkCache(source_file=wikilinks_file)

print(l_cache.get_links_from_entity(target_node))


print("Done!")
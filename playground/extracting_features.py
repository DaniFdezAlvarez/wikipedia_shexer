from wikipedia_shexer.utils.wikipedia_utils import WikipediaUtils
from wikipedia_shexer.features.feature_extractor import FeatureExtractor
from wikipedia_shexer.model.ontology import Ontology
from wikipedia_shexer.utils.cache import TypingCache, BackLinkCache

typing_file = "files\\guadalquivir_types.nt"
wikilinks_file = "files\\guadalquivir_links.nt"
# typing_file = "C:\\Users\\Dani\\Documents\\EII\\doctorado\\papers_propios\\wikipedia_shexer\\instance-types_lang_en_transitive.ttl"
# wikilinks_file = "C:\\Users\\Dani\\Documents\\EII\\doctorado\\papers_propios\\wikipedia_shexer\\wikilinks_lang_en.ttl"

i = 0

i += 1
print(i) # 1
ontology = Ontology(source_file="files\\dbpedia_2014.owl")

i += 1
print(i) # 2
t_cache = TypingCache(source_file=typing_file,
                      ontology=ontology,
                      filter_out_of_dbpedia=True,
                      discard_superclasses=True)

i += 1
print(i) # 3
l_cache = BackLinkCache(source_file=wikilinks_file)


i = 0
print(i) # 4
model_abstract = WikipediaUtils.extract_model_abstract(page_id="Guadalquivir",
                                                       inverse=True)


i += 1
print(i) # 5
f_extractor = FeatureExtractor(ontology=ontology,
                               type_cache=t_cache,
                               backlink_cache=l_cache)

i += 1
print(i) # 6
model_rows = f_extractor.rows_from_abstract(abstract=model_abstract)

i += 1
print(i)  # 7
result = f_extractor.serialize_rows(model_rows,str_return=True)

i += 1
print(i)  # 8

print(result)
print("Done!")




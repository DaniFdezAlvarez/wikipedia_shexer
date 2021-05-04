from wikipedia_shexer.utils.wikipedia_utils import WikipediaUtils
from wikipedia_shexer.features.feature_extractor import FeatureExtractor
from wikipedia_shexer.model.ontology import Ontology
from wikipedia_shexer.utils.cache import TypingCache, BackLinkCache
from wikipedia_shexer.io.csv_line_yielder import CSVYielderQuotesFilter
from wikipedia_shexer.io.line_reader.file_line_reader import FileLineReader

typing_file = "files\\guadalquivir_types.nt"
wikilinks_file = "files\\guadalquivir_links.nt"
dest_path = "files\\wikirows.csv"
target_instances_path = "files\\lakes_of_minnesota.csv"
# typing_file = "C:\\Users\\Dani\\Documents\\EII\\doctorado\\papers_propios\\wikipedia_shexer\\instance-types_lang_en_transitive.ttl"
# wikilinks_file = "C:\\Users\\Dani\\Documents\\EII\\doctorado\\papers_propios\\wikipedia_shexer\\wikilinks_lang_en.ttl"

i = 0

i += 1
print(i) # 1
ontology = Ontology(source_file="files\\dbpedia_2014.owl")
for a_p in ontology.properties_with_domran:
    print(a_p)
print(len(ontology.properties_with_domran))
i += 1
print(i) # 2
t_cache = TypingCache(source_file=typing_file,
                      ontology=ontology,
                      filter_out_of_dbpedia=True,
                      discard_superclasses=True)

i += 1
print(i) # 3
l_cache = BackLinkCache(source_file=wikilinks_file)


i += 1
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
uris_yielder = CSVYielderQuotesFilter(FileLineReader(source_file=target_instances_path))
target_instances = uris_yielder.list_lines()

i += 1
print(i)  # 7
f_extractor.rows_to_file_from_page_list(page_list=target_instances,
                                        inverse=True,
                                        file_path=dest_path)

print("Done!")




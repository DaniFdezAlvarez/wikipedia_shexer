from wikipedia_shexer.utils.wikidata_dbpedia_conversor import WikidataDBpediaConversor
from wikipedia_shexer.utils.wikidata_utils import WikidataUtils

conversor = WikidataDBpediaConversor()
# print(len(conversor._dbpedia_prop_to_wikidata))

wikicosas = WikidataUtils.find_wikidata_entities_in_wikipedia_page("Madrid")
print(wikicosas)


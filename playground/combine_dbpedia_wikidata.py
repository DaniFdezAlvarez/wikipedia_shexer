from wikipedia_shexer.utils.wikidata_dbpedia_conversor import WikidataDBpediaPropertyConversor, WikidataDBpediaEntItyConversor
from wikipedia_shexer.utils.wikidata_utils import WikidataUtils
from wikipedia_shexer.utils.dbpedia_utils import DBpediaUtils

# conversor = WikidataDBpediaPropertyConversor()
# print(len(conversor._dbpedia_prop_to_wikidata))

# wikicosas = WikidataUtils.find_wikidata_entities_in_wikipedia_page("Madrid")
# print(wikicosas)

# WikidataDBpediaEntItyConversor.wikidata_ID_to_DBpedia_ID("Q2807")


# WikidataUtils.find_tuples_of_a_wikipedia_page(page_id="Q2807")
dbo_success = []
wikidata_success = []

dbo_tuples = DBpediaUtils.find_tuples_of_a_wikipedia_page(page_id="Madrid",
                                                          just_summary=True)

wiki_s = WikidataDBpediaEntItyConversor.dbpedia_uri_to_wikidata_uri(dbo_tuples[0][0])
for a_tuple in dbo_tuples:
    prop_d = DBpediaUtils.get_property_linking_sub_and_obj(subj_uri=a_tuple[0],
                                                         obj_uri=a_tuple[1])
    if prop_d is not None:
        dbo_success.append((a_tuple[0], prop_d, a_tuple[1]))

    wiki_o = WikidataDBpediaEntItyConversor.dbpedia_uri_to_wikidata_uri(a_tuple[1])
    if wiki_o is not None:
        prop_w = WikidataUtils.get_property_linking_sub_and_obj(subj_uri=wiki_s,
                                                              obj_uri=wiki_o)
        if prop_w is not None:
            print(prop_w)
            wikidata_success.append((wiki_s, prop_w, wiki_o))

print(len(dbo_success), "dbo")
print(len(wikidata_success), "wikidata")





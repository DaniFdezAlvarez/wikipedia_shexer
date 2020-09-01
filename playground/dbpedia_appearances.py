from wikipedia_shexer.utils.dbpedia_utils import DBpediaUtils
from wikipedia_shexer.model.ontology import Ontology

ontology_path = "files\\dbpedia_2014.owl"

# dbrs = DBpediaUtils.find_dbo_entities_in_wikipedia_page(page_id="Madrid",
#                                                         just_summary=True)
# print("---")
# for a_dbr in dbrs:
#     print(a_dbr)
#     print(DBpediaUtils.get_types_of_a_dbpedia_node(a_dbr))

tuples = DBpediaUtils.find_tuples_of_a_wikipedia_page(page_id="Madrid",
                                                      just_summary=True)
# print(dbo_tuples)

for a_tuple in tuples:
    prop = DBpediaUtils.get_property_linking_sub_and_obj(subj_uri=a_tuple[0],
                                                         obj_uri=a_tuple[1])
    print(a_tuple, prop)
    # result = DBpediaUtils.get_properties_matching_with_subj_and_obj(subj_uri=a_tuple[0],
    #                                                                 obj_uri=a_tuple[1],
    #                                                                 ontology=Ontology(ontology_path))
    #
    # print(result)
    print("#######")

    # http: // dbpedia.org / resource / https: // en.wiktionary.orgmonocentric
    # http: // dbpedia.org / resource / Help: IPA / Spanish
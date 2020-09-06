from wikipedia_shexer.utils.wikidata_dbpedia_conversor import WikidataDBpediaPropertyConversor, WikidataDBpediaEntItyConversor
from wikipedia_shexer.utils.wikidata_utils import WikidataUtils
from wikipedia_shexer.utils.dbpedia_utils import DBpediaUtils
import json

from playground.consts import MENTIONED_ENTITIES, DBO_SUCCESS, DBO_DIRECT, WIKIDATA_DIRECT, \
    DBO_INVERSE, WIKIDATA_INVERSE, WIKIDATA_SUCCESS, WIKIDATA_MISSED_ENTITY, \
    WIKIDATA_MISSED_PROP, WIKIDATA_TRANSLATION

#CONFIG
target_entities = ["Jesús_Gil", "Madrid", "Cristiano_Ronaldo", "Billy_Talent", "Linkin Park", "Pikachu", "Nile", "Guadiana",
                   "Grand_Theft_Auto_V", "The_Office_(American_TV_series)", "Hamlet", "Zipi_y_Zape", "Bob_Dylan",
                   "Euphoria_(Loreen_song)", "Donald_Trump", "Langreo", "Rafael_Nadal", "Alfonso_Reyes_(basketball)", "Elephant",
                   "Electronic_Arts", "Aikido", "Japan", "Burkina_Faso", "Basketball", "Central_Park", "Mount_Everest", "Teide",
                   "Aneto", "Arecaceae", "Severe_acute_respiratory_syndrome_coronavirus_2", "Wuhan", "Microsoft", "Microsoft_Office",
                   "Jean-Claude_Van_Damme", "Super_Mario", "Leonardo_da_Vinci", "Francisco_Goya", "Mona_Lisa", "Saturn_Devouring_His_Son",
                   "Asturias", "Wisconsin"]
# target_entities = ["Pikachu"]
result_path = "toy_examples.json"




conversor_p = WikidataDBpediaPropertyConversor()
# print(len(conversor._dbpedia_prop_to_wikidata))

# wikicosas = WikidataUtils.find_wikidata_entities_in_wikipedia_page("Madrid")
# print(wikicosas)

# WikidataDBpediaEntItyConversor.wikidata_ID_to_DBpedia_ID("Q2807")


# WikidataUtils.find_tuples_of_a_wikipedia_page(page_id="Q2807")
dbo_success = []
wikidata_success = []
direct_dbo = [0]
direct_wikidata = [0]
wikidata_translation_count = [0]
dbpedia_mentions_without_wikidata_id = 0
number_of_tuples = 0


final_results = {}


def manage_properties_found(direct, inverse, source, target_list, target_count_direct,
                            wikidata_mode=False,
                            wikidata_translation=None):
    if direct is None and inverse is None:
        print("{0}: fail.".format(source))
    elif direct is not None and inverse is None:
        print("{0}: direct. {1}". format(source, direct))
        target_list.append(direct)
        target_count_direct[0] += 1
        if wikidata_mode:
            if conversor_p.wikidata_prop_to_dbo_prop(direct) is not None:
                wikidata_translation[0] += 1
    elif direct is None and inverse is not None:
        print("{0}: inverse. {1}".format(source, inverse))
        target_list.append(inverse)
        if wikidata_mode:
            if conversor_p.wikidata_prop_to_dbo_prop(inverse) is not None:
                wikidata_translation[0] += 1
    else:
        print("{0}: Double kill! : direct {1}, inverse {2}".format(source, direct, inverse))
        target_list.append(direct)
        if wikidata_mode:
            if conversor_p.wikidata_prop_to_dbo_prop(inverse) is not None \
                    or conversor_p.wikidata_prop_to_dbo_prop(direct) is not None:
                wikidata_translation[0] += 1
        target_count_direct[0] += 1




def store_results(page_id):
    final_results[page_id] = {
        MENTIONED_ENTITIES : number_of_tuples,
        DBO_SUCCESS : len(dbo_success),
        DBO_DIRECT : direct_dbo[0],
        WIKIDATA_DIRECT : direct_wikidata[0],
        DBO_INVERSE : len(dbo_success) - direct_dbo[0],
        WIKIDATA_INVERSE : len(wikidata_success) - direct_wikidata[0],
        WIKIDATA_SUCCESS : len(wikidata_success),
        WIKIDATA_MISSED_ENTITY : dbpedia_mentions_without_wikidata_id,
        WIKIDATA_TRANSLATION : wikidata_translation_count[0]
    }
    print("Mira esto")
    print(number_of_tuples)
    print(len(dbo_success))

def print_results(page_id):
    print("------------------------")
    print(page_id)
    print("----")
    for a_key, a_value in final_results[page_id].items():
        print(a_key, ":", a_value)


def serialize_results():
    with open(result_path, "w") as out_stream:
        json.dump(final_results, out_stream, indent=2)

def explore_entity(page_id):
    global dbo_success
    dbo_success = []
    global wikidata_success
    wikidata_success = []
    global direct_dbo
    direct_dbo = [0]
    global direct_wikidata
    direct_wikidata = [0]
    global wikidata_translation_count
    wikidata_translation_count = [0]
    global dbpedia_mentions_without_wikidata_id
    dbpedia_mentions_without_wikidata_id = 0
    dbo_tuples = DBpediaUtils.find_tuples_of_a_wikipedia_page(page_id=page_id,
                                                              just_summary=True)
    global number_of_tuples
    number_of_tuples = len(dbo_tuples)
    if len(dbo_tuples) > 0 :
        wiki_s = WikidataDBpediaEntItyConversor.dbpedia_uri_to_wikidata_uri(dbo_tuples[0][0])
    for a_tuple in dbo_tuples:
        print(direct_dbo[0], direct_wikidata[0])
        print(a_tuple[1])
        prop_d_d = DBpediaUtils.get_property_linking_sub_and_obj(subj_uri=a_tuple[0],
                                                                 obj_uri=a_tuple[1])
        prop_d_i = DBpediaUtils.get_property_linking_sub_and_obj(subj_uri=a_tuple[1],
                                                                 obj_uri=a_tuple[0])
        manage_properties_found(direct=prop_d_d,
                                inverse=prop_d_i,
                                source="DBpedia",
                                target_list=dbo_success,
                                target_count_direct=direct_dbo)

        wiki_o = WikidataDBpediaEntItyConversor.dbpedia_uri_to_wikidata_uri(a_tuple[1])
        if wiki_o is not None:
            prop_w_d = WikidataUtils.get_property_linking_sub_and_obj(subj_uri=wiki_s,
                                                                      obj_uri=wiki_o)
            prop_w_i = WikidataUtils.get_property_linking_sub_and_obj(subj_uri=wiki_o,
                                                                      obj_uri=wiki_s)
            manage_properties_found(direct=prop_w_d,
                                    inverse=prop_w_i,
                                    source="Wikidata",
                                    target_list=wikidata_success,
                                    target_count_direct=direct_wikidata,
                                    wikidata_mode=True,
                                    wikidata_translation=wikidata_translation_count)
        else:
            print("Wikidata fail. Not even an entity here", dbpedia_mentions_without_wikidata_id + 1)
            dbpedia_mentions_without_wikidata_id += 1

    store_results(page_id)
    print_results(page_id)


for a_page in target_entities:
    try:
        explore_entity(page_id=a_page)
    except BaseException as e:
        print("###################################################################")
        print("WWAAARRRNINNNGGG Algo fue petamal con" , a_page)
        print("###################################################################")

serialize_results()






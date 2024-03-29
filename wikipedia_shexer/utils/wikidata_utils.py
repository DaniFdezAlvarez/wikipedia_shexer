import requests
from wikipedia_shexer.utils.wikipedia_utils import WikipediaUtils
from wikipedia_shexer.utils.sparql import query_endpoint_single_variable
from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import page_id_to_DBpedia_id, dbpedia_id_to_page_title
from wikipedia_shexer.utils.dbpedia_utils import DBpediaUtils
from wikipedia_shexer.utils.const import WIKIDATA_NAMESPACE, WIKIDATA_SPARQL_ENDPOINT, \
    LEN_WIKIDATA_NAMESPACE, API_WIKIPEDIA



LINKING_RELATION_QUERY = """
SELECT ?p WHERE {{
    <{0}> ?p <{1}>
}}
"""



class WikidataUtils(object):

    @staticmethod
    def find_tuples_of_a_wikipedia_page(page_id, just_summary=True):
        """

        Tuples are returned as DBpedia dbo_tuples
        :param page_id:
        :param just_summary:
        :return:
        """
        mentioned_entities = WikidataUtils.find_wikidata_entities_in_wikipedia_page(page_id=page_id,
                                                                                    just_summary=just_summary)
        dbpdia_page_id = page_id_to_DBpedia_id(page_id)
        result = []
        for an_entity in mentioned_entities:
            result.append((dbpdia_page_id, WikidataUtils.wikidata_id_of_a_wikidata_uri(an_entity)))
        return result

    @staticmethod
    def get_property_linking_sub_and_obj(subj_uri, obj_uri):
        result = query_endpoint_single_variable(endpoint_url=WIKIDATA_SPARQL_ENDPOINT,
                                                str_query=LINKING_RELATION_QUERY.format(subj_uri,
                                                                                        obj_uri),
                                                variable_id="p",
                                                fake_user_agent=False)
        DBpediaUtils._remove_stop_properties(result)
        if len(result) == 0:
            return None
        if len(result) == 1:
            return result[0]
        else:
            print("WARNING: {0} and {1} are linked with more than one property. What should we do?".format(subj_uri, obj_uri))
            return result[0]
        #                                                                                                    obj_uri))
        # raise RuntimeError("{0} and {1} are linked with more than one property. What should we do?".format(subj_uri,
        #                                                                                                    obj_uri))


    @staticmethod
    def wikidata_id_of_a_wikidata_uri(wikidata_uri):
        """
        It assumes that the received uri is a correct wikidata one.

        :return:
        """
        return wikidata_uri[LEN_WIKIDATA_NAMESPACE:]

    @staticmethod
    def find_wikidata_entities_in_wikipedia_page(page_id, just_summary=True):
        html_content = WikipediaUtils.html_text_of_a_page(title=page_id,
                                                          just_summary=just_summary)
        return WikidataUtils.find_wikidata_entities_in_wikipedia_html_content(html_content=html_content)


    @staticmethod
    def find_wikidata_entities_in_wikipedia_html_content(html_content):

        candidates = [WikidataUtils.find_wikidata_id_for_a_page(dbpedia_id_to_page_title(a_dbpedia_id))
                      for a_dbpedia_id in DBpediaUtils.find_dbo_entities_in_wikipedia_html_content(html_content)]

        return [WikidataUtils.wikidata_entity_id_to_wikidata_entity_URL(elem) for elem in candidates if elem is not None]

    @staticmethod
    def wikidata_entity_id_to_wikidata_entity_URL(wikidata_id):
        return WIKIDATA_NAMESPACE + wikidata_id

    @staticmethod
    def find_wikidata_id_for_a_page(title_page):
        params = {
            'action': 'query',
            'prop': 'pageprops',
            'titles': title_page,
            'format': 'json'
        }
        r = requests.get(API_WIKIPEDIA, params=params)
        result_query = r.json()['query']
        pages = result_query['pages'] if 'pages' in result_query else None

        if pages is None:
            return None

        page_id = None if len(pages) != 1 else list(pages.keys())[0]
        if page_id is None:
            return None
        return pages[page_id]['pageprops']['wikibase_item'] \
            if 'pageprops' in pages[page_id] and 'wikibase_item' in pages[page_id]['pageprops'] \
            else None
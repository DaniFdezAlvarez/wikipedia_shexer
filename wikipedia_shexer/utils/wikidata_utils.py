import requests
from wikipedia_shexer.utils.wikipedia_utils import WikipediaUtils
from wikipedia_shexer.utils.dbpedia_utils import DBpediaUtils

API_WIKIPEDIA = "https://en.wikipedia.org/w/api.php?"
WIKIDATA_NAMESPACE = "http://www.wikidata.org/entity/"
LEN_WIKIDATA_NAMESPACE = len(WIKIDATA_NAMESPACE)



class WikidataUtils(object):

    @staticmethod
    def find_tuples_of_a_wikipedia_page(page_id, just_summary=True):
        """

        Tuples are returned as DBpedia tuples
        :param page_id:
        :param just_summary:
        :return:
        """
        mentioned_entities = WikidataUtils.find_wikidata_entities_in_wikipedia_page(page_id=page_id,
                                                                                    just_summary=just_summary)
        dbpdia_page_id = DBpediaUtils.page_id_to_DBpedia_id(page_id)
        result = []
        print("Que pacha")
        for an_entity in mentioned_entities:
            print("Mira pacha esto", an_entity)
            result.append((dbpdia_page_id, WikidataUtils.wikidata_id_of_a_wikidata_uri(an_entity)))
        return result

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

        candidates = [WikidataUtils.find_wikidata_id_for_a_page(DBpediaUtils.dbpedia_id_to_page_title(a_dbpedia_id))
                      for a_dbpedia_id in DBpediaUtils.find_dbo_entities_in_wikipadia_html_content(html_content)]

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
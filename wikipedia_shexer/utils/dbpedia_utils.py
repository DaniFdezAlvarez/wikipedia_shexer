from wikipedia_shexer.utils.wikipedia_utils import WikipediaUtils
from wikipedia_shexer.utils.sparql import query_endpoint_single_variable

DBPEDIA_EN_BASE = "http://dbpedia.org/resource/"

TYPE_QUERY = """
select ?o WHERE {{
   <{0}> rdf:type ?o
}}
"""

DBPEDIA_SPARQL_ENDPOINT = "https://dbpedia.org/sparql"

class DBpediaUtils(object):

    @staticmethod
    def find_dbo_entities_in_wikipedia_page(page_id, just_summary=False):
        html_content = WikipediaUtils.html_text_of_a_page(title=page_id,
                                                          just_summary=just_summary)
        return DBpediaUtils.find_dbo_entities_in_wikipadia_html_content(html_content=html_content)

    @staticmethod
    def find_dbo_entities_in_wikipadia_html_content(html_content):
        wikilinks = WikipediaUtils.wikilinks_in_html_content(html=html_content)
        result = set()
        for a_wikilink in wikilinks:
            page_link = a_wikilink.attrs['href'] if 'href' in a_wikilink.attrs else None
            page_link = page_link.replace("/wiki/", "") if page_link is not None else None
            if page_link is not None:
                result.add(DBpediaUtils.page_id_to_DBpedia_id(page_link))
        return result

    @staticmethod
    def page_id_to_DBpedia_id(page_id):
        return DBPEDIA_EN_BASE + page_id

    @staticmethod
    def get_types_of_a_dbpedia_node(dbp_node):
        return query_endpoint_single_variable(endpoint_url=DBPEDIA_SPARQL_ENDPOINT,
                                              str_query=TYPE_QUERY.format(dbp_node),
                                              variable_id="o",
                                              fake_user_agent=False)


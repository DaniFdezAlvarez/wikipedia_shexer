from wikipedia_shexer.utils.wikipedia_utils import WikipediaUtils
from wikipedia_shexer.utils.sparql import query_endpoint_single_variable
from wikipedia_shexer.utils.const import DBPEDIA_SPARQL_ENDPOINT
from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import html_wikilink_to_dbpedia_id, page_id_to_DBpedia_id


TYPE_QUERY = """
select ?o WHERE {{
   <{0}> rdf:type ?o
}}
"""

LINKING_RELATION_QUERY = """
SELECT ?p WHERE {{
    <{0}> ?p <{1}>
}}
"""

STOP_PROPERTIES = ["http://dbpedia.org/ontology/wikiPageWikiLink",
                   "http://www.w3.org/2000/01/rdf-schema#seeAlso"]



class DBpediaUtils(object):


    @staticmethod
    def find_true_triples_in_an_abstract(abstract, inverse=True):
        """
        It receives and abstract object and, mention by mention, it queries DBPedia looking for
        triples linking the target page and a mention.

        If inverse is active, it will look for triples where the target page can be subject or object.
        Otherwise, the target page will be just used as subject

        It returns a list of tuples containing those triles?


        :param page_id:
        :return:
        """
        if inverse:
            return DBpediaUtils._find_direct_triples_in_an_abstract(abstract)
        else:
            return DBpediaUtils._find_direct_and_inverse_triples_in_an_abstract(abstract)


    @staticmethod
    def get_property_linking_sub_and_obj(subj_uri, obj_uri):
        result = query_endpoint_single_variable(endpoint_url=DBPEDIA_SPARQL_ENDPOINT,
                                                str_query=LINKING_RELATION_QUERY.format(subj_uri,
                                                                                        obj_uri),
                                                variable_id="p",
                                                fake_user_agent=False)
        DBpediaUtils._remove_stop_properties(result)
        if len(result) == 0:
            return None
        if len(result) == 1:
            return result[0]
        # print(result)
        print("{0} and {1} are linked with more then one property. What should we do?".format(subj_uri,
                                                                                              obj_uri))
        return result[0]

    @staticmethod
    def find_dbo_entities_in_wikipedia_page(page_id, just_summary=True):
        html_content = WikipediaUtils.html_text_of_a_page(title=page_id,
                                                          just_summary=just_summary)
        return DBpediaUtils.find_dbo_entities_in_wikipedia_html_content(html_content=html_content)

    @staticmethod
    def find_dbo_entities_in_wikipedia_html_content(html_content):
        wikilinks = WikipediaUtils.wikilinks_in_html_content(html=html_content)
        result = set()
        for a_wikilink in wikilinks:
            # page_link = a_wikilink.attrs['href'] if 'href' in a_wikilink.attrs else None
            # page_link = page_link.replace("/wiki/", "") if page_link is not None else None
            # if page_link is not None:
            #     result.add(DBpediaUtils.page_id_to_DBpedia_id(page_link))
            dbpedia_id = html_wikilink_to_dbpedia_id(a_wikilink)
            if dbpedia_id is not None:
                result.add(dbpedia_id)
        return result


    @staticmethod
    def get_types_of_a_dbpedia_node(dbp_node, exclude_yago=True):
        result = query_endpoint_single_variable(endpoint_url=DBPEDIA_SPARQL_ENDPOINT,
                                                str_query=TYPE_QUERY.format(dbp_node),
                                                variable_id="o",
                                                fake_user_agent=False)
        if exclude_yago:
            result = [a_type for a_type in result if "/yago/" not in a_type]
        return result

    @staticmethod
    def find_tuples_of_a_wikipedia_page(page_id, just_summary=True):
        mentioned_entities = DBpediaUtils.find_dbo_entities_in_wikipedia_page(page_id=page_id,
                                                                              just_summary=just_summary)
        dbpdia_page_id = page_id_to_DBpedia_id(page_id)
        result = []
        for an_entity in mentioned_entities:
            result.append((dbpdia_page_id, an_entity))
        return result


    @staticmethod
    def get_properties_matching_with_subj_and_obj(subj_uri, obj_uri, ontology):
        subj_types = DBpediaUtils.get_types_of_a_dbpedia_node(subj_uri)
        obj_types = DBpediaUtils.get_types_of_a_dbpedia_node(obj_uri)
        result = set()
        # print("--------", subj_uri, obj_uri)
        for an_s_type in subj_types:
            for an_o_type in obj_types:
                # print(an_s_type, an_o_type)
                for elem in ontology.get_properties_matching_domran(an_s_type, an_o_type):
                    result.add(elem)
        return list(result)

    @staticmethod
    def _remove_stop_properties(list_properties):
        for a_prop in STOP_PROPERTIES:
            if a_prop in list_properties:
                list_properties.remove(a_prop)

    @staticmethod
    def _find_direct_and_inverse_triples_in_an_abstract(abstract):
        result = []
        page_uri = page_id_to_DBpedia_id(abstract.page_id)
        for a_mention in abstract.mentions():
            mention_uri = page_id_to_DBpedia_id(a_mention.entity_id)
            prop_d = DBpediaUtils.get_property_linking_sub_and_obj(subj_uri=page_uri,
                                                                   obj_uri=mention_uri)
            if prop_d is not None:
                result.append((page_uri, prop_d, mention_uri))
            else:
                prop_i = DBpediaUtils.get_property_linking_sub_and_obj(subj_uri=mention_uri,
                                                                       obj_uri=page_uri)
                if prop_i is not None:
                    result.append((mention_uri, prop_i, page_uri))
        return result

    @staticmethod
    def _find_direct_triples_in_an_abstract(abstract):
        result = []
        subj = page_id_to_DBpedia_id(abstract.page_id)
        for a_mention in abstract.mentions():
            obj = page_id_to_DBpedia_id(a_mention.entity_id)
            prop = DBpediaUtils.get_property_linking_sub_and_obj(subj_uri=subj,
                                                                 obj_uri=obj)
            if prop is not None:
                result.append((subj, prop, obj))
        return result



    @staticmethod
    def _find_inverse_triples_in_an_abstract(abstract):
        result = []
        obj = page_id_to_DBpedia_id(abstract.page_id)
        for a_mention in abstract.mentions():
            subj = page_id_to_DBpedia_id(a_mention.entity_id)
            prop = DBpediaUtils.get_property_linking_sub_and_obj(subj_uri=subj,
                                                                 obj_uri=obj)
            if prop is not None:
                result.append((subj, prop, obj))
        return result


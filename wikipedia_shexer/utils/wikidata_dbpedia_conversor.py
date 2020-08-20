from wikipedia_shexer.utils.sparql import query_endpoint_several_variables
from wikipedia_shexer.utils.dbpedia_utils import DBPEDIA_SPARQL_ENDPOINT

DBPEDIA_PROPS_QUERY = """
PREFIX       owl:  <http://www.w3.org/2002/07/owl#>
PREFIX      rdfs:  <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?DBpediaProp ?WikidataProp
WHERE
  {
    ?DBpediaProp  owl:equivalentProperty  ?WikidataProp .
                  FILTER ( CONTAINS ( str(?WikidataProp) , 'wikidata' ) ) .
  }
ORDER BY  ?DBpediaProp
"""

DBPEDIA_PROPS_VARIABLES = [ "DBpediaProp", "WikidataProp"]


WIKIDATA_PROPS_QUERY = """
PREFIX       wdt:  <http://www.wikidata.org/prop/direct/>
PREFIX  wikibase:  <http://wikiba.se/ontology#>
PREFIX        bd:  <http://www.bigdata.com/rdf#>

SELECT ?WikidataProp ?DBpediaProp
WHERE
  {
    ?WikidataProp  wdt:P1628  ?DBpediaProp .
    FILTER ( CONTAINS ( str(?DBpediaProp) , 'dbpedia' ) ) .
  }
"""

WIKIDATA_PROPS_VARIABLES = [ "WikidataProp", "DBpediaProp"]

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org"

class WikidataDBpediaConversor(object):

    def __init__(self):
        self._wikidata_prop_to_dbpedia = {}
        self._dbpedia_prop_to_wikidata = {}
        self._load_property_tables()



    def _load_property_tables(self):
        self._load_wikidata_equivalences()
        self._load_dbpedia_equivalences()

    def _load_prop_equivalence(self, dbpedia_prop, wikidata_prop):
        if dbpedia_prop in self._dbpedia_prop_to_wikidata:
            if wikidata_prop != self._dbpedia_prop_to_wikidata[dbpedia_prop]:
                raise ValueError("Conflict! Property disagreement")
            else:
                return
        self._dbpedia_prop_to_wikidata = wikidata_prop
        self._wikidata_prop_to_dbpedia = dbpedia_prop

    def _load_wikidata_equivalences(self):
        result = query_endpoint_several_variables(endpoint_url=WIKIDATA_SPARQL_ENDPOINT,
                                                  str_query=WIKIDATA_PROPS_QUERY,
                                                  variables=WIKIDATA_PROPS_VARIABLES)
        for i in range(0, len(result[WIKIDATA_PROPS_VARIABLES[0]])):
            normalized_dbpedia_prop = self._normalize_dbpedia_prop_if_needed(result[WIKIDATA_PROPS_VARIABLES[1]][i])
            self._load_prop_equivalence(dbpedia_prop=normalized_dbpedia_prop,  # Dbpedia
                                        wikidata_prop=result[WIKIDATA_PROPS_VARIABLES[0]][i])  # Wikidata

    def _normalize_dbpedia_prop_if_needed(self, dbpedia_prop):
        target_char_index = dbpedia_prop.rfind("/") + 1
        if not dbpedia_prop[target_char_index].isupper():
            return dbpedia_prop
        return dbpedia_prop[:target_char_index] + \
               dbpedia_prop[target_char_index].upper() + \
               dbpedia_prop[target_char_index+1:]



    def _load_dbpedia_equivalences(self):
        result = query_endpoint_several_variables(endpoint_url=DBPEDIA_SPARQL_ENDPOINT,
                                                  str_query=DBPEDIA_PROPS_QUERY,
                                                  variables=DBPEDIA_PROPS_VARIABLES)
        for i in range(0, len(result[DBPEDIA_PROPS_VARIABLES[0]])):
            self._load_prop_equivalence(dbpedia_prop=result[DBPEDIA_PROPS_VARIABLES[0]][i],  # Dbpedia
                                        wikidata_prop=result[DBPEDIA_PROPS_VARIABLES[1]][i])  # Wikidata

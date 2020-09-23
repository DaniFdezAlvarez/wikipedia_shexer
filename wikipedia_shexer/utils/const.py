from wikipedia_shexer.model.rdf import Property

API_WIKIDATA = "https://www.wikidata.org/w/api.php"
API_WIKIPEDIA = "https://en.wikipedia.org/w/api.php?"

DBPEDIA_SPARQL_ENDPOINT = "https://dbpedia.org/sparql"
DBPEDIA_EN_BASE = "http://dbpedia.org/resource/"

DBPEDIA_ONTOLOGY_NAMESPACE = "http://dbpedia.org/ontology/"


WIKIDATA_NAMESPACE = "http://www.wikidata.org/entity/"
WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
LEN_WIKIDATA_NAMESPACE = len(WIKIDATA_NAMESPACE)

WIKIPEDIA_EN_BASE = "https://en.wikipedia.org/wiki/"

RDF_TYPE = Property("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

S = 0
P = 1
O = 2
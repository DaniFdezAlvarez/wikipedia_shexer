from wikipedia_shexer.utils.wikipedia_utils import WikipediaUtils
from wikipedia_shexer.utils.dbpedia_utils import DBpediaUtils

result = WikipediaUtils.extract_model_abstract("Madrid")
tuples = DBpediaUtils.find_true_triples_in_an_abstract(result)
print("--------")
for a_tuple in tuples:
    print(a_tuple)

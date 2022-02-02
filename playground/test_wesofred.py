from wikipedia_shexer.wesofred.wes_fredapi import WesFredApi
from playground.config import API_KEY
BASE = 51

api = WesFredApi(api_key=API_KEY,petitions_already_performed=BASE)
sentence = "Metallica is the best heavymetal band that has ever played in Badalona"
result = api.get_rdflib_graph(sentence)
for a_triple in result.triples((None, None, None)):
    print("{} , {} , {}".format(a_triple[0], a_triple[1], a_triple[2]))
print("Done!")
from wikipedia_shexer.utils.wikipedia_utils import WikipediaUtils
from wikipedia_shexer.features.feature_extractor import FeatureExtractor
from wikipedia_shexer.model.ontology import Ontology

i = 0
print(i) # 0
model_abstract = WikipediaUtils.extract_model_abstract(page_id="Los_Punsetes",
                                                       inverse=True)
i += 1
print(i) # 1
ontology = Ontology(source_file="files\\dbpedia_2014.owl")

i += 1
print(i) # 2
f_extractor = FeatureExtractor(ontology=ontology)

i += 1
print(i) # 3
model_rows = f_extractor.rows_from_abstract(abstract=model_abstract)

i += 1
print(i)  # 4
result = f_extractor.serialize_rows(model_rows,str_return=True)

i += 1
print(i)  # 5

print(result)
print("Done!")




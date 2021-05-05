# from wikipedia_shexer.utils.dbpedia_utils import DBpediaUtils
from wikipedia_shexer.utils.class_importance import find_important_pr_nodes

in_cr_file = "C:\\Users\\Dani\\Documents\\EII\\doctorado\\PAPERS_PROPIOS\\wikipedia_shexer\\datasets\\classrank_dbpedia.json"
in_pr_file = "C:\\Users\\Dani\\Documents\\EII\\doctorado\\PAPERS_PROPIOS\\wikipedia_shexer\\datasets\\pagerank_dbpedia2.json"

# i_classes = DBpediaUtils.find_important_classes(cr_scores_path=in_cr_file,
#                                                 top_k=200)
# print(i_classes)
print("--------")

i_instances = find_important_pr_nodes(pr_scores_path=in_pr_file, top_k=200000)


for elem in i_instances:
    print(elem)

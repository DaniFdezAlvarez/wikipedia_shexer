# from wikipedia_shexer.utils.dbpedia_utils import DBpediaUtils
from wikipedia_shexer.utils.class_importance import find_most_important_instances_for_classes
from wikipedia_shexer.model.ontology import Ontology
from wikipedia_shexer.io.json_io import write_obj_to_json

in_cr_file = "C:\\Users\\Dani\\Documents\\EII\\doctorado\\PAPERS_PROPIOS\\wikipedia_shexer\\datasets\\classrank_dbpedia.json"
in_pr_file = "C:\\Users\\Dani\\Documents\\EII\\doctorado\\PAPERS_PROPIOS\\wikipedia_shexer\\datasets\\pagerank_dbpedia2.json"
typings_path = "C:\\Users\\Dani\\Documents\\EII\\doctorado\\PAPERS_PROPIOS\\shexer_canonical\\dbpedia_test\\typesallM.ttl"
ontology_file = "files\\dbpedia_2014.owl"
onto = Ontology(source_file=ontology_file)



# i_classes = DBpediaUtils.find_important_classes(cr_scores_path=in_cr_file,
#                                                 top_k=200)
# print(i_classes)
# print("--------")
#
# i_instances = find_important_pr_nodes(pr_scores_path=in_pr_file, top_k=200000)
#
#
# for elem in i_instances:
#     print(elem)


result = find_most_important_instances_for_classes(cr_scores_path=in_cr_file,
                                                   pr_scores_path=in_pr_file,
                                                   top_k_per_class=300,
                                                   top_k_instance=6000000,
                                                   top_k_classes=150,
                                                   typings_path=typings_path,
                                                   ontology_obj=onto)

write_obj_to_json(target_obj=result,
                  out_path="300instances_from_200classes.json")

print("Done!")

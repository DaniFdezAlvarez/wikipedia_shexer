from wikipedia_shexer.utils.dbpedia_utils import DBpediaUtils

in_cr_file = "C:\\Users\\Dani\\Documents\\EII\\doctorado\\PAPERS_PROPIOS\\wikipedia_shexer\\datasets\\classrank_dbpedia.json"
in_pr_file = ""

i_classes = DBpediaUtils.find_important_classes(cr_scores_path=in_cr_file,
                                                top_k=200)

print(i_classes)

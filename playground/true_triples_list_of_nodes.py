from wikipedia_shexer.utils.wikipedia_utils import WikipediaUtils
from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import dbpedia_id_to_page_title
from wikipedia_shexer.model.ontology import Ontology
from wikipedia_shexer.io.json_io import read_json_obj_from_path


target_instances_path = r"files\lakes_of_minnesota.csv"
ontology_file = r"C:\Users\Dani\Documents\EII\doctorado\PAPERS_PROPIOS\wikipedia_shexer\datasets\ontology_dbo.nt"
important_nodes_path = r"C:\Users\Dani\Documents\EII\doctorado\PAPERS_PROPIOS\wikipedia_shexer\datasets\300instances_from_200classes.json"
true_triples_file = r"C:\Users\Dani\Documents\EII\doctorado\PAPERS_PROPIOS\wikipedia_shexer\datasets\out\300_200_true_triples.nt"
true_triples_domram_file = r"C:\Users\Dani\Documents\EII\doctorado\PAPERS_PROPIOS\wikipedia_shexer\datasets\out\300_200_true_tripleswith_domran.nt"
node_counts_file = r"C:\Users\Dani\Documents\EII\doctorado\PAPERS_PROPIOS\wikipedia_shexer\datasets\out\300_200_node_counts.tsv"


node_counts = []
true_triples = []
true_triples_with_domran = []
target_pages = set()

tmp_nodes = read_json_obj_from_path(important_nodes_path)
for a_class_group in tmp_nodes:
    for a_node in a_class_group[1]:
        target_pages.add(dbpedia_id_to_page_title(a_node))


ontology = Ontology(source_file=ontology_file, format="turtle")

counter = 0
for a_page in target_pages:
    try:
        counter += 1
        with_domram_d = 0
        with_domram_i = 0
        model_abstract = WikipediaUtils.extract_model_abstract(page_id=a_page,
                                                               inverse=True)
        for a_mention in model_abstract._true_inverse_mentions:
            a_triple = a_mention.true_triple
            true_triples.append(a_triple)
            if ontology.has_property_domran(a_triple[1]):
                with_domram_i += 1
                true_triples_with_domran.append(a_triple)

        for a_mention in model_abstract._true_direct_mentions:
            a_triple = a_mention.true_triple
            true_triples.append(a_triple)
            if ontology.has_property_domran(a_triple[1]):
                with_domram_d += 1
                true_triples_with_domran.append(a_triple)
        node_counts.append((a_page,
                            with_domram_d + with_domram_i,
                            with_domram_d,
                            with_domram_i,
                            model_abstract.n_true_mentions,
                            model_abstract.n_true_direct_mentions,
                            model_abstract.n_true_inverse_mentions))
    except BaseException as e:
        print("Error with", a_page, ":", str(e))
    if counter % 20 == 0:
        print(counter, a_page)
print("Done comp!")

with open(node_counts_file, "w") as out_stream:
    for a_row in node_counts:
        out_stream.write("\t".join(a_row)+"\n")

print("Done file1!")

with open(true_triples_file, "w") as out_stream:
    for a_triple in true_triples:
        out_stream.write(" ".join(a_triple)+"\n")

print("Done file2!")

with open(true_triples_domram_file, "w") as out_stream:
    for a_triple in true_triples_with_domran:
        out_stream.write(" ".join(a_triple) + "\n")

print("Done!")




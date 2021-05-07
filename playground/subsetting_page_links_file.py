import json
from wikipedia_shexer.io.graph.yielder.nt_triples_yielder_targets_filter import NtTriplesYielderTargetsFilter

important_nodes_path = r"C:\Users\Dani\Documents\EII\doctorado\PAPERS_PROPIOS\wikipedia_shexer\datasets\300instances_from_200classes.json"
links_file = r"C:\Users\Dani\Documents\EII\doctorado\PAPERS_PROPIOS\wikipedia_shexer\datasets\page_links_en.ttl"

target_iris = set()
with open(important_nodes_path, "r") as in_stream:
    target_obj = json.load(in_stream)
    for a_class_group in target_obj:
        for a_node in a_class_group[1]:
            target_iris.add(a_node)

print("Going for it!")
yielder = NtTriplesYielderTargetsFilter(target_iris=target_iris,
                                        source_file=links_file)
for a_triple in yielder.yield_triples():
    pass

print(yielder.yielded_triples)
print("Done!")

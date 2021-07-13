
from wikipedia_shexer.io.json_io import read_json_obj_from_path

in_file = r"C:\Users\Dani\Documents\EII\doctorado\PAPERS_PROPIOS\wikipedia_shexer\datasets\300instances_from_200classes.json"
out_file = r"F:\datasets\300from200_targets.csv"

def read_nodes_list(nodes_path):
    result = set()
    target_obj = read_json_obj_from_path(nodes_path)
    for a_list1 in target_obj:
        for elem in a_list1[1]:
            result.add(elem)
    return result

nodes_set = read_nodes_list(in_file)
with open(out_file, "w") as out_stream:
    for elem in nodes_set:
        out_stream.write(elem + "\n")

print("Done!")
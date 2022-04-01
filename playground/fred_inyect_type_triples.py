import json

RDF_TYPE = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
_S = 0
_P = 1
_O = 2

def load_json_dict(class_instances_file):
    result = {}
    with open(class_instances_file, "r", encoding="utf-8") as in_stream:
        json_obj = json.load(in_stream)
        for a_class_list in json_obj:
            tmp_set = set()
            result["<{}>".format(a_class_list[0])] = tmp_set
            for instance in a_class_list[1]:
                tmp_set.add("<{}>".format(instance))
    return result



def class_pattern_path(a_class, path_pattern):
    # Remove Wikipedia onto namespace and remove corners
    return path_pattern.format(a_class.replace("http://dbpedia.org/ontology/", "")[1:-1])


def load_instance_triples(a_class, instances, in_triples_pattern):
    result = {}
    with open(class_pattern_path(a_class=a_class,
                                 path_pattern=in_triples_pattern),
              "r",
              encoding="utf-8") as in_stream:
        for a_line in in_stream:
            pieces = a_line.strip().split(" ")
            if len(pieces) == 4 and pieces[_P] == RDF_TYPE and pieces[_S] in instances:
                if pieces[_S] not in result:
                    result[pieces[_S]] = set()
                result[pieces[_S]].add(pieces[_O])
    return result

def locate_needed_type_triples(dict_instance_triples, a_class):
    result = set()
    for instance, types in dict_instance_triples.items():
        if a_class not in types:
            result.add((instance, a_class))
    return result

def append_triples(a_class, triples_to_write, in_triples_pattern, out_triples_pattern):
    with open(class_pattern_path(a_class=a_class,
                                 path_pattern=out_triples_pattern),
              "w",
              encoding="utf-8") as out_stream:
        with open(class_pattern_path(a_class=a_class,
                                     path_pattern=in_triples_pattern),
                  "r",
                  encoding="utf-8") as in_stream:
            out_stream.write(in_stream.read())  # Write old content
            out_stream.write("\n")  # Write sep in case there wasnt one
            for a_tuple in triples_to_write:
                out_stream.write("{} {} {} .\n".format(a_tuple[0],
                                                       RDF_TYPE,
                                                       a_tuple[1]))


def inyect_class_types(a_class, instances, in_triples_pattern, out_triples_pattern):
    print("Going for {} ...".format(a_class))
    try:
        dict_instance_triples = load_instance_triples(a_class=a_class,
                                                      instances=instances,
                                                      in_triples_pattern=in_triples_pattern)
        triples_to_write = locate_needed_type_triples(dict_instance_triples=dict_instance_triples,
                                                      a_class=a_class)
        append_triples(a_class=a_class,
                       triples_to_write=triples_to_write,
                       in_triples_pattern=in_triples_pattern,
                       out_triples_pattern=out_triples_pattern)
        print("{} done!".format(a_class))
    except FileNotFoundError:
        print("Cant compute {}, no triples found.".format(a_class))


def run(class_instances_file, in_triples_pattern, out_triples_pattern):
    class_dict = load_json_dict(class_instances_file=class_instances_file)
    print("dict loaded...")
    for a_class, instances in class_dict.items():
        inyect_class_types(a_class, instances, in_triples_pattern, out_triples_pattern)


if __name__ == "__main__":
    run(class_instances_file=r"F:\datasets\300instances_from_200classes.json",
        in_triples_pattern=r"F:\datasets\fred\triples\{}.nt",
        out_triples_pattern=r"F:\datasets\fred\triples_extra_types\{}.nt")


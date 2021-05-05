from wikipedia_shexer.io.json_io import read_json_obj_from_path
from wikipedia_shexer.io.graph.yielder.nt_triples_yielder import NtTriplesYielder
from wikipedia_shexer.io.graph.yielder.base_triples_yielder import _S, _O

DBO_PREFIX = "http://dbpedia.org/ontology/"

def find_important_pr_nodes(pr_scores_path, top_k):
    """
    Receives nodes and its pagerank score and it returns a sorted list containing the top_k most
    important nodes according to PR.

    The input elements are not expected to be sorted
    Structure expected for the input pagerank scores:

    {
     "http://i1": 0.2,
     "http://i2": 0.3,
     "http://i3": 0.00982,
     ...
     "http://in": 1.34e-08

    :param pr_scores_path:
    :param top_k:
    :return: list nodes (URIs) sorted by decreasing importance
    """
    return [elem[0] for elem in find_important_pr_nodes_and_scores(pr_scores_path=pr_scores_path,
                                                                   top_k=top_k)]

def find_important_pr_nodes_and_scores(pr_scores_path, top_k):
    """
    Receives nodes and its pagerank score and it returns a sorted list containing the top_k most
    important nodes according to PR.

    The input elements are not expected to be sorted
    Structure expected for the input pagerank scores:

    {
     "http://i1": 0.2,
     "http://i2": 0.3,
     "http://i3": 0.00982,
     ...
     "http://in": 1.34e-08

    :param pr_scores_path:
    :param top_k:
    :return: list of 2-tuples. The 1st elem is the URI, the second elem is the PR score.
    The elements are sorted (decreasing importance)
    """
    result = []
    target_tmp_size = (top_k / 2) + 1
    counter = 0
    tmp = []
    with open(pr_scores_path) as in_stream:
        for a_line in in_stream:
            a_line = a_line.strip()
            if a_line.startswith('"'):
                counter += 1
                # Check tmp is full
                if counter % target_tmp_size == 0:
                    result = result + tmp
                    if len(result) > top_k:
                        result.sort(reverse=True, key=lambda x: x[1])
                        result = result[:top_k]
                    tmp = []
                # Parse line
                i_separation = a_line.find('": ')
                an_uri = a_line[1:i_separation]
                a_score = a_line[i_separation + 3:]
                if a_score.endswith(","):
                    a_score = a_score[:-1]
                a_score = float(a_score)
                tmp.append( (an_uri, a_score) )
    result = result + tmp
    if len(result) > top_k:
        result.sort(reverse=True, key=lambda x: x[1])
        result = result[:top_k]
    return result



def find_important_cr_classes(cr_scores_path, top_k=100, from_dbo=True):
    """
    Ir returns a list of classes sorted by descending importance according to classrank.
    The number of classes is indicated with "top_k".
    If 'from_dbo' is set to True, URIs not in the dbpedia ontology are excluded from the results

    Expected format of classrank_scores:
    [
       [ "http://dbpedia.org/ontology/class1",  # class URI
          1.0,                                  # normalized CR score
          1                                     # pos in ranking
        ],
        [ "http://dbpedia.org/ontology/class1",
          0.776,
          2
        ]
    ...
    ]

    :param cr_scores: path to a json_list_of_classrank_scores
    :param top_k: number of classes
    :return:
    """
    json_obj = read_json_obj_from_path(target_path=cr_scores_path)

    if not from_dbo:
        return [a_class_obj[0] for a_class_obj in json_obj[:min(top_k, len(json_obj))]]
    tmp = [a_class_obj[0] for a_class_obj in json_obj if a_class_obj[0].startswith(DBO_PREFIX)]
    return tmp[:min(top_k, len(tmp))]


def find_direct_typings_for_nodes(target_nodes, typings_path, from_dbo=True):
    result = {a_node : set() for a_node in target_nodes}

    for a_triple in NtTriplesYielder(source_file=typings_path).yield_triples():
        if a_triple[_S].iri in result:
            if not from_dbo or a_triple[_O].iri.startswith(DBO_PREFIX):
                result[a_triple[_S].iri].add(a_triple[_O].iri)
    return result



def find_all_typing_for_target_nodes(direct_typings_dict, ontology):
    """
    It modifies the direct typings dict. And it also returns it. Wierd, isn't it? :3

    :param direct_typings_dict:
    :param ontology:
    :return:
    """

    for a_class, its_types in direct_typings_dict.items():
        tmp = []
        for a_type in its_types:
            tmp += ontology.get_sorted_superclasses(a_type)
        its_types |= set(tmp)
    return direct_typings_dict


def find_most_important_instances_for_classes(cr_scores_path, pr_scores_path, top_k_per_class,
                                              top_k_instance, top_k_classes, typings_path, ontology_obj):
    """

    It returns a list of lists, with the top_k_per_class most_important instances for each target class according to PR.
    An isntance will only be part of the results if it at least between the top_k_instance most important instances
    with PR.


    Expected format:
    [ [
        "uri_class1",
        [
            "1_best_instance_uri_class1",    # instance URI
            "2_best_instance_uri_class1",
            "3_best_instance_uri_class1",
            ...
            "top_k_per_class_best_instance_uri_class1"
        ]
      ],
      [
        "uri_class2",
        [
            "1_best_instance_uri_class2",    # instance URI
            "2_best_instance_uri_class2",
            "3_best_instance_uri_class2",
            ...
            "top_k_per_class_best_instance_uri_class1"
        ]
      ],

      ....


      [
        "uri_class_len(target_class)",
        [
            "1_best_instance_uri_class_len(target_class)",    # instance URI
            "2_best_instance_uri_class_len(target_class)",
            "3_best_instance_uri_class_len(target_class)",
            ...
            "top_k_per_class_best_instance_uri_class1"
        ]
      ],

    ]

    :param cr_scores_path:
    :param pr_scores_path:
    :param top_k_per_class:
    :param top_k_instance:
    :param top_k_classes:
    :param typings_path:
    :param ontology_obj:
    :return:
    """

    target_classes = find_important_cr_classes(cr_scores_path=cr_scores_path,
                                               top_k=top_k_classes,
                                               from_dbo=True)

    tmp_class_results = {uri_class : [] for uri_class in target_classes}
    def_class_results = {}
    potential_target_instances = find_important_pr_nodes(pr_scores_path=pr_scores_path,
                                                         top_k=top_k_instance)

    typings = find_direct_typings_for_nodes(target_nodes=potential_target_instances,
                                            typings_path=typings_path,
                                            from_dbo=True)

    typings = find_all_typing_for_target_nodes(direct_typings_dict=typings,
                                               ontology=ontology_obj)

    for an_instance in potential_target_instances:
        for a_type in typings[an_instance]:
            if a_type in tmp_class_results:
                tmp_class_results[a_type].append(an_instance)
                if len(tmp_class_results[a_type]) == top_k_per_class:
                    def_class_results[a_type] = tmp_class_results[a_type]
                    del tmp_class_results[a_type]
                    if len(tmp_class_results) == 0:
                        break

    print("Incomplete!")
    for a_type in tmp_class_results:
        print(a_type, len(tmp_class_results[a_type]))
        def_class_results[a_type] = tmp_class_results[a_type]
    tmp_class_results = None  # Free memory

    result = []
    for a_class in target_classes:
        result.append([
            a_class,
            def_class_results[a_class]
        ])
    return result

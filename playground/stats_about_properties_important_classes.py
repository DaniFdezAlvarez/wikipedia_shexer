from wikipedia_shexer.io.json_io import read_json_obj_from_path

# TT ---> True Triples

AVG_TT = "AVG_TT"
AVG_DTT = "AVG_DTT"
AVG_ITT = "AVG_ITT"

N_INSTANCES = "n_instances"

MAX_S_TT = "MAX_S_TT"
MAX_U_TT = "MAX_U_TT"
MAX_S_DTT = "MAX_S_DTT"
MAX_U_DTT = "MAX_U_DTT"
MAX_S_ITT = "MAX_S_ITT"
MAX_U_ITT = "MAX_U_ITT"

MIN_S_TT = "MIN_S_TT"
MIN_U_TT = "MIN_U_TT"
MIN_S_DTT = "MIN_S_DTT"
MIN_U_DTT = "MIN_U_DTT"
MIN_S_ITT = "MIN_S_ITT"
MIN_U_ITT = "MIN_U_ITT"

AVG_DM = "AVG_DM"
AVG_DDM = "AVG_DDM"
AVG_IDM = "AVG_IDM"

# DM --> DOMRAN. Counts w.r.t. the number of true triples with properties hving well-defined domran
MAX_S_DM = "MAX_S_DM"
MAX_U_DM = "MAX_U_DM"
MAX_S_DDM = "MAX_S_DDM"
MAX_U_DDM = "MAX_U_DDM"
MAX_S_IDM = "MAX_S_IDM"
MAX_U_IDM = "MAX_U_IDM"

MIN_S_DM = "MIN_S_DM"
MIN_U_DM = "MIN_U_DM"
MIN_S_DDM = "MIN_S_DDM"
MIN_U_DDM = "MIN_U_DDM"
MIN_S_IDM = "MIN_S_IDM"
MIN_U_IDM = "MIN_U_IDM"


SEPARATOR = "\t"
POS_URI = 0
POS_TT = 1
POS_DTT = 2
POS_ITT = 3
POS_DM = 4
POS_DDM = 5
POS_IDM = 6

AVG_KEY_PAIRS = [
    (POS_TT, AVG_TT),
    (POS_ITT, AVG_ITT),
    (POS_DTT, AVG_DTT),
    (POS_DM, AVG_DM),
    (POS_IDM, AVG_DDM),
    (POS_IDM, AVG_DDM),

]

MAX_KEYS_POS_SCORE_URI = {
    (POS_DM, MAX_S_DM, MAX_U_DM),
    (POS_IDM, MAX_S_IDM, MAX_U_IDM),
    (POS_IDM, MAX_S_DDM, MAX_U_DDM),
    (POS_TT, MAX_S_TT, MAX_U_TT),
    (POS_ITT, MAX_S_ITT, MAX_U_ITT),
    (POS_DTT, MAX_S_DTT, MAX_U_DTT),

}


MIN_KEYS_POS_SCORE_URI = {
    (POS_DM,  MIN_S_DM,  MIN_U_DM),
    (POS_IDM, MIN_S_IDM, MIN_U_IDM),
    (POS_IDM, MIN_S_DDM, MIN_U_DDM),
    (POS_TT,  MIN_S_TT,  MIN_U_TT),
    (POS_ITT, MIN_S_ITT, MIN_U_ITT),
    (POS_DTT, MIN_S_DTT, MIN_U_DTT),

}

RANK_TT = "RANKING_TT"

SORTED_RESULT_KEYS = [AVG_TT,
                      AVG_DTT,
                      AVG_ITT,
                      AVG_DM,
                      AVG_DDM,
                      AVG_IDM,
                      MAX_S_TT,
                      MAX_S_DTT,
                      MAX_S_ITT,
                      MAX_S_DM,
                      MAX_S_DDM,
                      MAX_S_IDM,
                      MIN_S_TT,
                      MIN_S_DTT,
                      MIN_S_ITT,
                      MIN_S_DM,
                      MIN_S_DDM,
                      MIN_S_IDM,
                      MAX_U_TT,
                      MAX_U_DTT,
                      MAX_U_ITT,
                      MAX_U_DM,
                      MAX_U_DDM,
                      MAX_U_IDM,
                      MIN_U_TT,
                      MIN_U_DTT,
                      MIN_U_ITT,
                      MIN_U_DM,
                      MIN_U_DDM,
                      MIN_U_IDM
                      ]

def complete_instances_dict(class_uri, class_instances, instances_dict):
    for an_instance in class_instances:
        if an_instance not in instances_dict:
            instances_dict[an_instance] = []
        instances_dict[an_instance].append(class_uri)


def init_class_dict(class_uri, class_features, n_instances):
    class_features[class_uri] = {
        N_INSTANCES: n_instances,
        MAX_S_TT: 0,
        MAX_U_TT: None,
        MAX_S_DTT: 0,
        MAX_U_DTT: None,
        MAX_S_ITT: 0,
        MAX_U_ITT: None,
        MIN_S_TT: 0,
        MIN_U_TT: None,
        MIN_S_DTT: 0,
        MIN_U_DTT: None,
        MIN_S_ITT: 0,
        MIN_U_ITT: None,
        MAX_S_DM: 0,
        MAX_U_DM: None,
        MAX_S_DDM: 0,
        MAX_U_DDM: None,
        MAX_S_IDM: 0,
        MAX_U_IDM: None,
        MIN_S_DM: 0,
        MIN_U_DM: None,
        MIN_S_DDM: 0,
        MIN_U_DDM: None,
        MIN_S_IDM: 0,
        MIN_U_IDM: None,
        AVG_DM: 0,
        AVG_DDM: 0,
        AVG_IDM: 0,
        AVG_TT: 0,
        AVG_DTT: 0,
        AVG_ITT: 0
    }


def add_avg_values_to_class(pieces, class_uri, class_features):
    t_dict = class_features[class_uri]
    for pos_pieces, key_dict in AVG_KEY_PAIRS:
        t_dict[key_dict] += pieces[pos_pieces]


def compute_min_values(pieces, class_uri, class_features):
    t_dict = class_features[class_uri]
    instance_uri = pieces[POS_URI]
    for pos_pieces, key_score, key_uri in MIN_KEYS_POS_SCORE_URI:
        if t_dict[key_uri] is None or t_dict[key_score] > pieces[pos_pieces]:
            t_dict[key_score] = pieces[pos_pieces]
            t_dict[key_uri] = instance_uri


def compute_max_values(pieces, class_uri, class_features):
    t_dict = class_features[class_uri]
    instance_uri = pieces[POS_URI]
    for pos_pieces, key_score, key_uri in MAX_KEYS_POS_SCORE_URI:
        if t_dict[key_score] < pieces[pos_pieces]:
            t_dict[key_score] = pieces[pos_pieces]
            t_dict[key_uri] = instance_uri


def add_features_to_class(pieces, class_uri, class_features):
    add_avg_values_to_class(pieces, class_uri, class_features)
    compute_min_values(pieces, class_uri, class_features)
    compute_max_values(pieces, class_uri, class_features)


def process_tt_lines(pieces, class_features, instances_dict):
    for a_class in instances_dict:
        add_features_to_class(pieces, a_class, class_features)
        compute_max_values(pieces, a_class, class_features)
        compute_min_values(pieces, a_class, class_features)

def compute_averages(class_features):
    for a_class_dict in class_features.values():
        if a_class_dict[N_INSTANCES] > 0:
            for pos_pieces, dict_key in AVG_KEY_PAIRS:
                a_class_dict[dict_key] = float(a_class_dict[dict_key]) / a_class_dict[N_INSTANCES]


def write_results(class_features, dest_path):
    sorted_result = []


    for class_uri, class_dict in class_features.items():
        sorted_result.append(
            [0] + [class_dict[a_key] for a_key in SORTED_RESULT_KEYS]
        )
    sorted_result.sort(reverse=True, key=lambda x:x[1])
    counter = 1
    with open(dest_path, "w") as out_stream:
        out_stream.write("#" + SEPARATOR.join([RANK_TT] + SORTED_RESULT_KEYS) + "\n")
        for array_line in sorted_result:
            array_line[0] = counter
            counter += 1
            out_stream.write(SEPARATOR.join(sorted_result) + "\n")


def init_dicts(json_obj, instances_dict, class_features):
    for a_class_group in json_obj:
        class_uri = a_class_group[0]
        class_instances = a_class_group[1]

        complete_instances_dict(class_uri, class_instances, instances_dict)
        init_class_dict(class_uri, class_features, len(class_instances))


def process_frequencies(tt_instances_file, instances_dict, class_features):
    with open(tt_instances_file, "r") as in_stream:
        for a_line in in_stream:
            pieces = a_line.strip().split(SEPARATOR)
            process_tt_lines(pieces, class_features, instances_dict)

def run():
    important_classes_file = r""
    tt_instances_file = r""
    out_file = r""
    instances_dict = {}
    class_features = {}

    #read json_target_obj
    json_obj = read_json_obj_from_path(important_classes_file)

    # Init main structures
    init_dicts(json_obj, instances_dict, class_features)

    # Process prop frequency
    process_frequencies(tt_instances_file, instances_dict, class_features)

    # Compute averages
    compute_averages(class_features)

    # Write results
    write_results(class_features, out_file)

    print("Done!")

if __name__ == "__main__":
    run()

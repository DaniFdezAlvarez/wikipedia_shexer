import json
from typing import Generator

CLASS_POSITION_IC_FILE = 0
INSTANCE_LIST_POSITION_IC_FILE = 1
INSTANCE_POSITION_FEATURE_ROW = 1


def load_target_dicts(i_c_file: str) -> (dict, dict):
    i_c_dict = {}
    class_lines_dict = {}
    with open(i_c_file, "r", encoding="utf-8") as in_stream:
        json_obj = json.load(in_stream)
        for a_class_list in json_obj:
            class_simple = a_class_list[CLASS_POSITION_IC_FILE].replace("http://dbpedia.org/ontology/","")
            class_lines_dict[class_simple] = []
            for an_instnace in a_class_list[INSTANCE_LIST_POSITION_IC_FILE]:
                instance_simple = an_instnace.replace("http://dbpedia.org/resource/", "")
                if instance_simple not in i_c_dict:
                    i_c_dict[instance_simple] = []
                i_c_dict[instance_simple].append(class_simple)
    return i_c_dict, class_lines_dict


def yield_feature_lines(feature_file: str) -> Generator[str, None, None]:
    with open(feature_file, "r", encoding="utf-8") as in_stream:
        for a_line in in_stream:
            a_line = a_line.strip()
            if a_line != "" and not a_line.startswith("prop;"):
                yield a_line.strip()

def process_features_files(features_file: str, i_c_dict: dict, class_lines_dict: dict) -> None:
    print("Starting line processing...")
    counter = 0
    for a_line in yield_feature_lines(features_file):
        counter += 1
        pieces = a_line.split(";")
        for a_class in i_c_dict[pieces[INSTANCE_POSITION_FEATURE_ROW]]:
            class_lines_dict[a_class].append(a_line)
        if counter % 100000 == 0:
            print("{} lines processed...".format(counter))
    # That's it, no need to return


def serialize_lines(class_lines_dict: dict, file_pattern: str) -> None:
    for a_class, lines_list in class_lines_dict.items():
        with open(file_pattern.format(a_class), "w", encoding="utf-8") as out_stream:
            out_stream.write("\n".join(lines_list))


def run(features_file: str, i_c_file: str, out_file_pattern: str) -> None:
    print("Starting...")
    i_c_dict, class_lines_dict = load_target_dicts(i_c_file)
    print("Base structures loaded...")
    process_features_files(features_file=features_file,
                           i_c_dict=i_c_dict,
                           class_lines_dict=class_lines_dict)
    print("Features distributed by class...")
    serialize_lines(class_lines_dict=class_lines_dict,
                    file_pattern=out_file_pattern)
    print("Everything serialized...")
    print("Done!")

if __name__ == "__main__":
    run(features_file=r"F:\datasets\300from200_all_CANDIDATE_features.csv",
        i_c_file=r"F:\datasets\300instances_from_200classes.json",
        out_file_pattern=r"F:\datasets\sliced_features\{}_candidate_features.csv")
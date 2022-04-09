import os

def count_lines_file(file_name):
    counter = 0
    with open(file_name, "r", encoding="utf-8") as in_str:
        for a_line in in_str:
            if a_line.strip() != "":
                counter += 1
    return counter

def count_lines_dir(dir_name, extension=""):
    counter = 0
    for root, dirs, files in os.walk(dir_name):
        for name in files:
            if name.endswith(extension):
                counter += count_lines_file(file_name=os.path.join(root, name))
    return counter


def count_properties_file(file_name, initial_set=None):
    result_set = initial_set if initial_set is not None else set()
    with open(file_name, "r", encoding="utf-8") as in_str:
        for a_line in in_str:
            if a_line.strip() != "":
                a_line = a_line.split(" ")
                result_set.add(a_line[1])  # property position
    return result_set

def count_properties_dir(dir_name, extension=""):
    target_set = set()
    for root, dirs, files in os.walk(dir_name):
        for name in files:
            if name.endswith(extension):
                target_set = count_properties_file(file_name=os.path.join(root, name),
                                                   initial_set=target_set)
    return len(target_set)

if __name__ == "__main__":
    # print(count_lines_dir(dir_name=r"F:\datasets\fred\triples_extra_types",
    #                       extension="nt"))  # 89971
    # print(count_properties_dir(dir_name=r"F:\datasets\fred\triples_extra_types",
    #                            extension="nt"))  # 2723
    print(count_properties_dir(dir_name=r"F:\datasets\seitma_l\no_training\not_sliced",
                               extension="ttl"))  # 21


    print("Done!")
import json

def run(in_file_path : str, out_file_path: str) -> None:
    with open(in_file_path, "r", encoding="utf-8") as in_stream:
        target_obj = json.load(in_stream)
        target_instances = set()
        for a_class_list in target_obj:
            for an_instance in a_class_list[1]:  # 1 -> position of instance list
                target_instances.add(an_instance)
        with open(out_file_path, "w") as out_stream:
            out_stream.write("\n".join(
                elem.replace("http://dbpedia.org/resource/", "") for
                elem in target_instances)
            )

if __name__ == "__main__":
    target_json_file = r"F:\datasets\300instances_from_200classes.json"
    instances_out_file = r"F:\datasets\300from200_every_instance.csv"
    run(in_file_path=target_json_file,
        out_file_path=instances_out_file)
    print("Done!")



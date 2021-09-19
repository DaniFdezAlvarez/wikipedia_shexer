from wikipedia_shexer.io.graph.yielder.multi_yielder import MultiYielder
from wikipedia_shexer.io.graph.yielder.nt_triples_yielder import NtTriplesYielder
from wikipedia_shexer.io.graph.yielder.filters.just_iris_triple_yielder import JustIrisTriplesYielder
from wikipedia_shexer.io.graph.yielder.adapters.str_triples_yielder import StrTriplesYielder
import pandas as pd

_S = 0
_P = 1
_O = 2

_DIRECT = "D"
_INVERSE = "I"

_INSTANCE_CUP = 300


def get_yielder(source_files):
    base_yielders = [NtTriplesYielder(source_file=a_path) for a_path in source_files]
    return StrTriplesYielder(base_yielder=JustIrisTriplesYielder(
            MultiYielder(yielder_list=base_yielders)
        )
    )

def find_instances(props_dict, source_files):
    props_done = set()
    for a_triple in get_yielder(source_files).yield_triples():
        if a_triple[_P] in props_dict and a_triple[_P] not in props_done:
            remove = True
            if len(props_dict[a_triple[_P]][_DIRECT]) < _INSTANCE_CUP:
                props_dict[a_triple[_P]][_DIRECT].add(a_triple[_S])
                remove = False
            if len(props_dict[a_triple[_P]][_INVERSE]) < _INSTANCE_CUP:
                props_dict[a_triple[_P]][_INVERSE].add(a_triple[_O])
                remove = False
            if remove:
                print("zas!")
                props_done.add(a_triple[_P])
                print(len(props_done), ",", len(props_dict))
                if len(props_done) == len(props_dict):
                    print("Weeee")
                    break
    result = set()
    for prop_dict in props_dict.values():
        for directed_prop_set in prop_dict.values():
            for an_instance in directed_prop_set:
                result.add(an_instance)
    return result



def save_instances(target_path, instances):
    with open(target_path, "w", encoding="utf-8") as out_stream:
        out_stream.write("\n".join(instances))

def read_target_properties(csv_source):
    col_names = ["prop", "instance", "mention", "positive", "direct", "cand_abs",
                 "cand_sen", "rel_cand_abs", "rel_cand_sen", "ent_sen", "rel_ent_a",
                 "rel_ent_sen", "rel_sen_abs", "back_link"]
    features = pd.read_csv(csv_source, header=None, names=col_names, sep=";")
    return set(features['prop'])

def run(source_properties,
        sources_dump,
        target_path):
    target_properties = read_target_properties(csv_source=source_properties)
    prop_dict = {a_prop : {_DIRECT : set(), _INVERSE : set()} for a_prop in target_properties}
    instances = find_instances(props_dict=prop_dict,
                               source_files=sources_dump)
    save_instances(target_path=target_path,
                   instances=instances)

if __name__ == "__main__":
    source_properties = r"F:\datasets\300from200_row_features.csv"
    sources_dump = [r"F:\datasets\mappingbased-objects.ttl",
                    r"F:\datasets\infobox-properties_lang=en.ttl"]
    target_path = "target_instances.txt"
    run(source_properties=source_properties,
        sources_dump=sources_dump,
        target_path=target_path)
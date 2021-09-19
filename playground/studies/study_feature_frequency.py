from wikipedia_shexer.io.json_io import read_json_obj_from_path
from wikipedia_shexer.io.features.feature_yielder import FeatureYielder
from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import dbpedia_id_to_page_title
from wikipedia_shexer.io.csv import CSVSerializator


def build_instantiation_dict(c_i_obj):
    result = {}
    for a_class_list in c_i_obj:
        class_uri = a_class_list[0]
        for an_instance in a_class_list[1]:
            an_instance = dbpedia_id_to_page_title(an_instance)
            if an_instance not in result:
                result[an_instance] = set()
            result[an_instance].add(class_uri)
    print(len(result))
    return result


def yield_rows(rows_path):
    for a_row in FeatureYielder(rows_path=rows_path).yield_rows():
        yield a_row


_TOTAL_USAGE_PROP = "total times used"
_DIRECT_USAGE_PROP = "direct"
_INVERSE_USAGE_PROP = "inverse"
_POSOTIVE_USAGE_PROP = "positive"
_NEGATIVE_USAGE_PROP = "negative"
_DIRECT_POSITIVE_USAGE = "direct & positive"
_SINGLE_CANDIDATE_USAGE = "just positive examples in abstract"
_MULTIPLE_CANDIDATE_USAGE = "some negative examples in abstract"


def init_prop_entry(a_prop, prop_counts):
    prop_counts[a_prop] = {
        _TOTAL_USAGE_PROP: 0,
        _DIRECT_USAGE_PROP: 0,
        _INVERSE_USAGE_PROP: 0,
        _POSOTIVE_USAGE_PROP: 0,
        _NEGATIVE_USAGE_PROP: 0,
        _SINGLE_CANDIDATE_USAGE: 0,
        _MULTIPLE_CANDIDATE_USAGE: 0,
        _DIRECT_POSITIVE_USAGE : 0
    }


def annotate_prop_usage(row, prop_counts):
    target_prop = row.prop
    if target_prop not in prop_counts:
        init_prop_entry(target_prop, prop_counts)
    prop_counts[target_prop][_TOTAL_USAGE_PROP] += 1
    prop_counts[target_prop][_DIRECT_USAGE_PROP if row.direct else _INVERSE_USAGE_PROP] += 1
    prop_counts[target_prop][_POSOTIVE_USAGE_PROP if row.positive else _NEGATIVE_USAGE_PROP] += 1
    prop_counts[target_prop][
        _SINGLE_CANDIDATE_USAGE if row.n_candidates_in_abstract == 1 else _MULTIPLE_CANDIDATE_USAGE] += 1
    if row.positive and row.direct:
        prop_counts[target_prop][_DIRECT_POSITIVE_USAGE] += 1


_TOTAL_ROWS_CLASS = "total rows"
_ENTITIES_WITH_ROWS = "entities"
_TOTAL_DIRECT_ROWS = "direct rows"
_TOTAL_INVERSE_ROWS = "inverse rows"
_TOTAL_POSITIVE_ROWS = "positive rows"
_TOTAL_NEGATIVE_ROWS = "negative rows"
_DIRECT_POSITIVE_ROWS = "direct & positive rows"
_N_ENTITIES_WITH_ROWS = "n entities non-empty"
_AVG_ROWS_PER_ENTITY = "avg rows entity"
_AVG_ROWS_PER_NON_EMPTY_ENTITY = "avg rows non-empty entity"
_AVG_DIRECT_ROWS_PER_ENTITY = "avg direct rows"
_AVG_INVERSE_ROWS_PER_ENTITY = "avg inverse rows"
_AVG_POSITIVE_ROWS_PER_ENTITY = "avg positive rows"
_AVG_NEGATIVE_ROWS_PER_ENTITY = "avg negative rows"
_AVG_DIRECT_POSITIVE_ROWS = "avg direct positive rows"
_MAX_ROWS_OF_AN_ENTITY = "max rows of an entity"
_ENTITY_WITH_MAX_ROWS = "entity with max rows"


def init_class_entry(target_class,
                     c_i_counts):
    c_i_counts[target_class] = {
        _TOTAL_ROWS_CLASS: 0,
        _ENTITIES_WITH_ROWS: {},
        _TOTAL_DIRECT_ROWS: 0,
        _TOTAL_INVERSE_ROWS: 0,
        _TOTAL_POSITIVE_ROWS: 0,
        _TOTAL_NEGATIVE_ROWS: 0,
        _DIRECT_POSITIVE_ROWS: 0,
        _N_ENTITIES_WITH_ROWS: 0,
        _AVG_ROWS_PER_ENTITY: 0,
        _AVG_ROWS_PER_NON_EMPTY_ENTITY: 0,
        _AVG_DIRECT_ROWS_PER_ENTITY: 0,
        _AVG_INVERSE_ROWS_PER_ENTITY: 0,
        _AVG_POSITIVE_ROWS_PER_ENTITY: 0,
        _AVG_NEGATIVE_ROWS_PER_ENTITY: 0,
        _AVG_DIRECT_POSITIVE_ROWS: 0,
        _MAX_ROWS_OF_AN_ENTITY: 0,
        _ENTITY_WITH_MAX_ROWS: ""
    }


def annotate_instance_usage(a_class, an_instance, c_i_counts):
    if an_instance not in c_i_counts[a_class][_ENTITIES_WITH_ROWS]:
        c_i_counts[a_class][_ENTITIES_WITH_ROWS][an_instance] = 0
    c_i_counts[a_class][_ENTITIES_WITH_ROWS][an_instance] += 1


def annotate_class_usage(row, c_i_counts, instantiation_dict):
    target_classes = instantiation_dict[row.instance]
    for a_class in target_classes:
        if a_class not in c_i_counts:
            init_class_entry(target_class=a_class,
                             c_i_counts=c_i_counts)
        c_i_counts[a_class][_TOTAL_ROWS_CLASS] += 1
        c_i_counts[a_class][_TOTAL_DIRECT_ROWS if row.direct else _TOTAL_INVERSE_ROWS] += 1
        c_i_counts[a_class][_TOTAL_POSITIVE_ROWS if row.positive else _TOTAL_NEGATIVE_ROWS] += 1
        if row.positive and row.direct:
            c_i_counts[a_class][_DIRECT_POSITIVE_ROWS] += 1
        annotate_instance_usage(a_class=a_class,
                                an_instance=row.instance,
                                c_i_counts=c_i_counts)

def fill_aggregates_non_empty_class(target_class, c_i_counts, total_instances):
    c_i_counts[target_class][_AVG_ROWS_PER_ENTITY] = float(
        c_i_counts[target_class][_TOTAL_ROWS_CLASS]) / total_instances

    c_i_counts[target_class][_AVG_DIRECT_ROWS_PER_ENTITY] = float(
        c_i_counts[target_class][_TOTAL_DIRECT_ROWS]) / total_instances

    c_i_counts[target_class][_AVG_INVERSE_ROWS_PER_ENTITY] = float(
        c_i_counts[target_class][_TOTAL_INVERSE_ROWS]) / total_instances

    c_i_counts[target_class][_AVG_POSITIVE_ROWS_PER_ENTITY] = float(
        c_i_counts[target_class][_TOTAL_POSITIVE_ROWS]) / total_instances

    c_i_counts[target_class][_AVG_NEGATIVE_ROWS_PER_ENTITY] = float(
        c_i_counts[target_class][_TOTAL_NEGATIVE_ROWS]) / total_instances

    c_i_counts[target_class][_AVG_DIRECT_POSITIVE_ROWS] = float(
        c_i_counts[target_class][_DIRECT_POSITIVE_ROWS]) / total_instances

    c_i_counts[target_class][_AVG_ROWS_PER_NON_EMPTY_ENTITY] = float(
        c_i_counts[target_class][_TOTAL_ROWS_CLASS]) / len(c_i_counts[target_class][_ENTITIES_WITH_ROWS])

    c_i_counts[target_class][_N_ENTITIES_WITH_ROWS] = len(c_i_counts[target_class][_ENTITIES_WITH_ROWS])

    entities_dict = c_i_counts[target_class][_ENTITIES_WITH_ROWS]

    for an_entity_key in entities_dict:
        if entities_dict[an_entity_key] > c_i_counts[target_class][_MAX_ROWS_OF_AN_ENTITY]:
            c_i_counts[target_class][_MAX_ROWS_OF_AN_ENTITY] = entities_dict[an_entity_key]
            c_i_counts[target_class][_ENTITY_WITH_MAX_ROWS] = an_entity_key



def compute_c_i_aggregates(original_c_i_obj, c_i_counts):
    for a_class_list in original_c_i_obj:
        total_instances = len(a_class_list[1])
        if total_instances > 0:
            target_class = a_class_list[0]
            if target_class not in c_i_counts: # A class that will stay empty no productive entities. Empty results
                init_class_entry(target_class=target_class,
                                 c_i_counts=c_i_counts)
            else:
                fill_aggregates_non_empty_class(target_class=target_class,
                                                c_i_counts=c_i_counts,
                                                total_instances=total_instances)


def produce_output_props(out_path, prop_counts):
    result = []
    for prop_key, prop_dict in prop_counts.items():
        result.append([prop_key,                      # 0
                       prop_dict[_TOTAL_USAGE_PROP],  # 1
                       prop_dict[_DIRECT_USAGE_PROP],  # 2
                       prop_dict[_INVERSE_USAGE_PROP],  # 3
                       prop_dict[_POSOTIVE_USAGE_PROP],  # 4
                       prop_dict[_NEGATIVE_USAGE_PROP],  # 5
                       prop_dict[_SINGLE_CANDIDATE_USAGE],  # 6
                       prop_dict[_MULTIPLE_CANDIDATE_USAGE],  # 7
                       prop_dict[_DIRECT_POSITIVE_USAGE]  # 8
                       ])
    CSVSerializator.serialize_list_of_lists(out_file=out_path,
                                            list_of_lists=result,
                                            sep=";",
                                            sorting_field_index=1,
                                            headers_list=[
                                                "prop",
                                                _TOTAL_USAGE_PROP,
                                                _DIRECT_USAGE_PROP,
                                                _INVERSE_USAGE_PROP,
                                                _POSOTIVE_USAGE_PROP,
                                                _NEGATIVE_USAGE_PROP,
                                                _SINGLE_CANDIDATE_USAGE,
                                                _MULTIPLE_CANDIDATE_USAGE,
                                                _DIRECT_POSITIVE_USAGE
                                            ])

def produce_output_c_i(out_path, c_i_counts):
    result = []
    for class_key, class_dict in c_i_counts.items():
        result.append([class_key,  # 0
                       class_dict[_TOTAL_ROWS_CLASS],  # 1
                       class_dict[_DIRECT_POSITIVE_ROWS],  # 2
                       class_dict[_TOTAL_DIRECT_ROWS],  # 3
                       class_dict[_AVG_ROWS_PER_ENTITY],  # 4
                       class_dict[_AVG_ROWS_PER_NON_EMPTY_ENTITY],  # 5
                       class_dict[_TOTAL_NEGATIVE_ROWS],  # 6
#                       class_dict[_ENTITIES_WITH_ROWS],  #
                       class_dict[_N_ENTITIES_WITH_ROWS],  # 8 -1
                       class_dict[_TOTAL_INVERSE_ROWS],  # 9 - 1
                       class_dict[_TOTAL_POSITIVE_ROWS],  # 10  - 1
                       class_dict[_AVG_DIRECT_ROWS_PER_ENTITY],  # 11  - 1
                       class_dict[_AVG_INVERSE_ROWS_PER_ENTITY],  # 12  - 1
                       class_dict[_AVG_POSITIVE_ROWS_PER_ENTITY],  # 13 - 1
                       class_dict[_AVG_NEGATIVE_ROWS_PER_ENTITY],  # 14 - 1
                       class_dict[_AVG_DIRECT_POSITIVE_ROWS],  # 15 - 1
                       class_dict[_MAX_ROWS_OF_AN_ENTITY],  # 16 - 1
                       class_dict[_ENTITY_WITH_MAX_ROWS]  # 17 - 1
                       ])
    CSVSerializator.serialize_list_of_lists(out_file=out_path,
                                            list_of_lists=result,
                                            sep=";",
                                            sorting_field_index=1,
                                            headers_list=[
                                                "class",
                                                _TOTAL_ROWS_CLASS,
                                                _DIRECT_POSITIVE_ROWS,
                                                _TOTAL_DIRECT_ROWS,
                                                _AVG_ROWS_PER_ENTITY,
                                                _AVG_ROWS_PER_NON_EMPTY_ENTITY,
                                                _TOTAL_NEGATIVE_ROWS,
                                                _N_ENTITIES_WITH_ROWS,
                                                _TOTAL_INVERSE_ROWS,
                                                _TOTAL_POSITIVE_ROWS,
                                                _AVG_DIRECT_ROWS_PER_ENTITY,
                                                _AVG_INVERSE_ROWS_PER_ENTITY,
                                                _AVG_POSITIVE_ROWS_PER_ENTITY,
                                                _AVG_NEGATIVE_ROWS_PER_ENTITY,
                                                _AVG_DIRECT_POSITIVE_ROWS,
                                                _MAX_ROWS_OF_AN_ENTITY,
                                                _ENTITY_WITH_MAX_ROWS
                                            ])


def produce_output(out_props_path, out_class_path, prop_counts, c_i_counts):
    produce_output_props(out_path=out_props_path,
                         prop_counts=prop_counts)
    produce_output_c_i(out_path=out_class_path,
                       c_i_counts=c_i_counts)


def run(rows_path, classes_instances_path, out_props_path, out_class_path):
    c_i_obj = read_json_obj_from_path(classes_instances_path)
    instantiation_dict = build_instantiation_dict(c_i_obj)
    prop_counts = {}
    c_i_counts = {}
    c = 0
    for a_row in yield_rows(rows_path):
        annotate_prop_usage(row=a_row,
                            prop_counts=prop_counts)
        annotate_class_usage(row=a_row,
                             c_i_counts=c_i_counts,
                             instantiation_dict=instantiation_dict)
        c += 1
    print(c)
    compute_c_i_aggregates(original_c_i_obj=c_i_obj, c_i_counts=c_i_counts)
    produce_output(out_props_path=out_props_path,
                   out_class_path=out_class_path,
                   prop_counts=prop_counts,
                   c_i_counts=c_i_counts)


if __name__ == "__main__":
    run(rows_path=r"F:\datasets\300from200_row_features.csv",
        classes_instances_path=r"C:\Users\Dani\repos-git\wikipedia_shexer\playground\files\300instances_from_200classes.json",
        out_props_path=r"F:\datasets\300from200_sorted_props.csv",
        out_class_path=r"F:\datasets\300from200_sorted_c_i.csv")
    print("Done!")

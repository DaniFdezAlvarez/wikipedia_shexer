_HEADERS = "prop;instance;mention"
_COMPLETE_HEADERS = "prop;instance;mention;positive;direct;cand_abs;cand_sen;rel_cand_abs;rel_cand_sen;ent_sen;rel_ent_a;rel_ent_sen;rel_sen_abs;back_link"


def exclude_example_info(original_row):
    pieces = original_row.split(";")
    pieces = pieces[0:3] + pieces[4:]  # it removes the fourth column (positive)
    return ";".join(pieces)

def yield_rows(a_file):
    with open(a_file, "r", encoding="utf-8") as in_stream:
        for a_line in in_stream:
            a_line = a_line.strip()
            if not a_line.startswith(_HEADERS) and a_line != "":
                yield a_line


def build_set_out_of_file(a_file):
    result = set()
    for a_row in yield_rows(a_file):
        result.add(exclude_example_info(a_row))
    return result

def run(old_candidates_file, examples_file, new_candidates_file):
    set_examples = build_set_out_of_file(examples_file)

    originals = 0
    result = 0

    with open(new_candidates_file, "w", encoding="utf8") as out_stream:
        # out_stream.write(_COMPLETE_HEADERS + "\n")

        for a_row in yield_rows(old_candidates_file):
            originals += 1
            tunned_row = exclude_example_info(a_row)
            if not tunned_row in set_examples:
                result += 1
                out_stream.write(a_row + "\n")


    print("Total examples: {}".format(len(set_examples)))
    print("Originals: {}".format(originals))
    print("Result: {}".format(result))

    print("Percentage discarded: {}".
        format(
        (originals - result) * 1.0 / originals
    ))

    print("candidates vs examples: {}".
        format(
        (result) * 1.0 / len(set_examples)
    ))



if __name__ == "__main__":
    run(old_candidates_file=r"F:\datasets\300from200_all_CANDIDATE_features.csv",
        examples_file=r"F:\datasets\300from200_row_features.csv",
        new_candidates_file=r"F:\datasets\300from200_candidates_no_training_data_no_heads.csv")

    print("Done!")
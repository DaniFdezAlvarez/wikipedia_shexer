_HEADERS = "prop;instance;mention"


def yield_rows(a_file):
    with open(a_file, "r", encoding="utf-8") as in_stream:
        for a_line in in_stream:
            a_line = a_line.strip()
            if not a_line.startswith(_HEADERS) and a_line != "":
                pieces = a_line.split(";")
                pieces = pieces[0:3] + pieces[4:]  # it removes the fourth column (positive)
                yield ";".join(pieces)


def build_set_out_of_file(a_file):
    result = set()
    for a_row in yield_rows(a_file):
        result.add(a_row)
    return result

def run(candidates_file, examples_file):
    set_examples = build_set_out_of_file(examples_file)
    swapped = 0
    candidates_count = 0

    for a_row in yield_rows(candidates_file):
        candidates_count += 1
        if a_row in set_examples:
            swapped += 1


    print("Total candidates: {}".format(candidates_count))
    print("Total examples: {}".format(len(set_examples)))
    print("Swapped: {}".format(swapped))
    print("Percentaje of non-swapped examples: {}".
        format(
            (len(set_examples) - swapped)*1.0 / len(set_examples)
        )
    )
    print("Percentaje of swapped candidates: {}".
          format(
        swapped / candidates_count
    ))

if __name__ == "__main__":
    run(candidates_file=r"F:\datasets\300from200_all_CANDIDATE_features.csv",
        examples_file=r"F:\datasets\300from200_row_features.csv")

    print("Done!")
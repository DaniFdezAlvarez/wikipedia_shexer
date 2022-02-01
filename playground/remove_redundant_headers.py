in_file = r"F:\datasets\ontology_range_fixed\300from200_all_candidate_features_ontf.csv"
out_file = r"F:\datasets\ontology_range_fixed\300from200_all_candidate_features_ontf_no_heads.csv"

with open(in_file, "r", encoding="utf-8") as in_str:
    counter = 1
    with open(out_file, "w", encoding="utf-8") as out_str:
        nice_headers = in_str.readline()
        # out_str.write(nice_headers)
        for a_line in in_str:
            counter += 1
            if a_line != nice_headers:
                out_str.write(a_line)
            else:
                print("erased!", counter)
print("Done!")
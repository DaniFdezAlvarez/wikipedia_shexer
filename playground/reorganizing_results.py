from playground.consts import MENTIONED_ENTITIES, DBO_SUCCESS, DBO_DIRECT, WIKIDATA_DIRECT, \
    DBO_INVERSE, WIKIDATA_INVERSE, WIKIDATA_SUCCESS, WIKIDATA_MISSED_ENTITY, WIKIDATA_TRANSLATION

import json
source_path = "toy_examples.json"
csv_out = "toy_results.csv"

SORTED_KEADERS = [MENTIONED_ENTITIES, DBO_SUCCESS, DBO_DIRECT, DBO_INVERSE,
                  WIKIDATA_SUCCESS, WIKIDATA_DIRECT, WIKIDATA_INVERSE, WIKIDATA_TRANSLATION,
                  WIKIDATA_MISSED_ENTITY]


with open(source_path, "r") as in_stream:
    result_dict = json.load(in_stream)

with open(csv_out, "w") as out_stream:
    out_stream.write(";".join(SORTED_KEADERS) + "\n")

    for a_key, a_dict in result_dict.items():
        out_stream.write(a_key + ";")
        for a_header in SORTED_KEADERS:
            out_stream.write(str(a_dict[a_header]) + ";")
        out_stream.write("\n")

print("Done!")
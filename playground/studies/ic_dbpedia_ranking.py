
from shexer.io.graph.yielder.nt_triples_yielder import NtTriplesYielder

def run(typings_file):
    res = {}
    yielder = NtTriplesYielder(source_file=typings_file,
                               allow_untyped_numbers=True)
    for a_triple in yielder.yield_triples():
        str_class = str(a_triple[2])
        if str_class.startswith("http://dbpedia.org/ontology/"):
            if str_class not in res:
                res[str_class] =0
            res[str_class] += 1

    res = [(key, value) for key,value in res.items()]
    res.sort(reverse=True, key=lambda x:x[1])

    rank = 1
    for a_tuple in res:
        print("{}\t{}\t{}".format(rank, a_tuple[1], a_tuple[0]))
        rank += 1

    print("Done!")

if __name__ == "__main__":
    run(r"F:\datasets\instance-types_lang=en_specific.ttl")

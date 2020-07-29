from rdflib import Graph, RDF, OWL, RDFS

DOMAIN = 'dom'
RANGE = 'rang'

ontog = Graph()

ontog.load("files\\dbpedia_2014.owl")

counter = 0
props = {}
for triple in ontog.triples((None, RDF.type, OWL.ObjectProperty)):
    counter += 1
    props[triple[0]] = {DOMAIN : set(),
                        RANGE : set()}

counter_range = 0
counter_domain = 0
counter_both = 0

for a_prop in props:
    domain = range = False
    for a_triple in ontog.triples((a_prop, RDFS.domain, None)):
        props[a_prop][DOMAIN].add(str(a_triple[2]))
        counter_domain += 1
        domain = True



    for a_triple in ontog.triples((a_prop, RDFS.range, None)):
        props[a_prop][RANGE].add(str(a_triple[2]))
        counter_range += 1
        range = True
    if domain and range:
        counter_both += 1


    print(str(a_prop))
    print(props[a_prop])

print("Props", counter)
print("Range", counter_range)
print("Domain", counter_domain)
print("Both", counter_both)



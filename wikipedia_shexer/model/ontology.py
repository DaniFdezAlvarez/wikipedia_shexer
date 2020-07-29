from rdflib import Graph, RDF, OWL, RDFS

_DOMAIN_KEY = "d"
_RANGE_KEY = "r"

class Ontology(object):

    def __init__(self, source_file):
        self._source_file = source_file

        self._ontog = Graph()
        self._ontog.load(source_file)

        self._object_poperties = self._get_object_properties()
        self._object_properties_with_domran = []
        self._domran_dict = {}
        self._init_domrans()


    def _get_properties_matching_triple(self, subject_class, object_class):
        for a_property in self._object_properties_with_domran:
            target_prop_dict = self._domran_dict[str(a_property)]
            if self._matches_domain(target_prop_dict, subject_class) and  \
                self._matches_range(target_prop_dict, object_class):
                pass  # TODO TODO TODO

    def _get_object_properties(self):
        result = []
        for triple in self._ontog.triples((None, RDF.type, OWL.ObjectProperty)):
            result.append(triple[0])

    def _init_domrans(self):
        partial_dict = {}
        for a_prop in self._object_poperties:
            str_prop = str(a_prop)
            partial_dict[str_prop] = {_DOMAIN_KEY : set(),
                                      _RANGE_KEY : set()}
            domain = range = False
            for a_triple in self._ontog.triples((a_prop, RDFS.domain, None)):
                partial_dict[a_prop][_DOMAIN_KEY].add(str(a_triple[2]))
                domain = True


            for a_triple in self._ontog.triples((a_prop, RDFS.range, None)):
                partial_dict[a_prop][_DOMAIN_KEY].add(str(a_triple[2]))
                range = True

            if domain and range:
                self._domran_dict[str_prop] = {_DOMAIN_KEY: partial_dict[str_prop][_DOMAIN_KEY],
                                               _RANGE_KEY: partial_dict[str_prop][_RANGE_KEY]}

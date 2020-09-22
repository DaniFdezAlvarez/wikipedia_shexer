from wikipedia_shexer.io.graph.yielder.nt_triples_yielder import NtTriplesYielder
from wikipedia_shexer.utils.const import RDF_TYPE, S, P, O, DBPEDIA_EN_BASE
from wikipedia_shexer.model.rdf import Property
from wikipedia_shexer.utils.triple_yielders import check_is_property_belongs_to_namespace


class TypingCache(object):

    def __init__(self, source_file, ontology=None
                 , filter_out_of_dbpedia=True, discard_superclasses=True, instantiation_property=RDF_TYPE):

        self._ontology = ontology
        self._filter_not_dbpedia = filter_out_of_dbpedia
        self._discard_superclasses = discard_superclasses
        self._instantiation_property = instantiation_property if type(instantiation_property) == Property \
            else Property(instantiation_property)

        self._is_a_relevant_triple = self._decide_relevant_triple_func()  # Pythonized strategy pattern
        self._collapse_types = self._decide_collapse_types_func()  # Pythonized strategy pattern

        self._type_dict = {}
        self._load_type_cache(source_file)

    def get_types_of_node(self, a_node):
        if a_node in self._type_dict:
            return self._type_dict[a_node]
        return []

    def _decide_relevant_triple_func(self):
        return self._is_a_relevant_triple_dbpedia_filter \
            if self._filter_not_dbpedia \
            else self._is_a_relevant_triple_no_dbpedia_filter

    def _decide_collapse_types_func(self):
        return self._collapse_types_just_removing_repetitions \
            if not self._discard_superclasses \
            else self._collapse_types_discarding_superclasses

    def _collapse_types(self):
        raise NotImplementedError()  # It will be overwritten during the __init__

    def _collapse_types_discarding_superclasses(self):
        self._collapse_types_just_removing_repetitions()
        for a_key in self._type_dict:
            self._type_dict[a_key] = self._collapse_list_removing_superclasses(self._type_dict[a_key])

    def _collapse_list_removing_superclasses(self, a_list):
        superclasses = set()
        base_classes = set()
        for a_class in a_list:
            if a_class not in superclasses:
                for a_superclass in self._ontology.get_sorted_superclasses(a_class):
                    superclasses.add(a_superclass)
                    if a_superclass in base_classes:
                        base_classes.remove(a_superclass)
                base_classes.add(a_class)
        return list(base_classes)

    def _collapse_types_just_removing_repetitions(self):
        for a_key in self._type_dict:
            self._type_dict[a_key] = list(set(self._type_dict[a_key]))  # Removing duplicates without order

    def _load_type_cache(self, source_file):
        triple_yielder = NtTriplesYielder(source_file=source_file)
        for a_triple in triple_yielder.yield_triples():
            if self._is_a_relevant_triple(a_triple):
                self._annotate_triple(a_triple)
        self._collapse_types()

    def _is_a_relevant_triple(self, a_triple):
        raise NotImplementedError()  # It will be overwritten during the __init__

    def _is_a_relevant_triple_no_dbpedia_filter(self, a_triple):
        return a_triple[P] == self._instantiation_property

    def _is_a_relevant_triple_dbpedia_filter(self, a_triple):
        return self._is_a_relevant_triple_no_dbpedia_filter(a_triple) and self._is_a_dbpedia_type(a_triple[O])

    def _is_a_dbpedia_type(self, target_type):
        return check_is_property_belongs_to_namespace(str_prop=target_type.iri,
                                                      namespace=DBPEDIA_EN_BASE)

    def _annotate_triple(self, a_triple):
        subj = a_triple[S].iri
        obj = a_triple[O].iri

        if subj not in self._type_dict:
            self._type_dict[subj] = []
        self._type_dict[subj].append(obj)


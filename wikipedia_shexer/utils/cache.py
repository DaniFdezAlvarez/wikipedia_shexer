from wikipedia_shexer.io.graph.yielder.nt_triples_yielder import NtTriplesYielder
from wikipedia_shexer.utils.const import RDF_TYPE, S, P, O, DBPEDIA_ONTOLOGY_NAMESPACE, WIKILINK_PROPERTY
from wikipedia_shexer.model.rdf import Property, Iri
from wikipedia_shexer.utils.triple_yielders import check_if_uri_belongs_to_namespace

_S = 0
_P = 1
_O = 2


class TypingCache(object):

    def __init__(self, source_file, ontology=None, filter_out_of_dbpedia=True,
                 discard_superclasses=True, instantiation_property=RDF_TYPE):

        self._ontology = ontology
        self._filter_not_dbpedia = filter_out_of_dbpedia
        self._discard_superclasses = discard_superclasses
        self._instantiation_property = instantiation_property if type(instantiation_property) == Property \
            else Property(instantiation_property)

        self._is_a_relevant_triple = self._decide_relevant_triple_func()  # Pythonized strategy pattern
        self._collapse_types = self._decide_collapse_types_func()  # Pythonized strategy pattern

        self._type_dict = {}
        self._load_type_cache(source_file)

    def get_types_of_node(self, node):
        if node in self._type_dict:
            return self._type_dict[node]
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
        return check_if_uri_belongs_to_namespace(str_uri=target_type.iri,
                                                 namespace=DBPEDIA_ONTOLOGY_NAMESPACE)

    def _annotate_triple(self, a_triple):
        subj = a_triple[S].iri
        obj = a_triple[O].iri

        if subj not in self._type_dict:
            self._type_dict[subj] = []
        self._type_dict[subj].append(obj)


class DestFilteredTypingCache(TypingCache):

    def __init__(self, source_file, target_iris, ontology=None, filter_out_of_dbpedia=True,
                 discard_superclasses=True, instantiation_property=RDF_TYPE):
        super().__init__(source_file=source_file,
                         ontology=ontology,
                         filter_out_of_dbpedia=filter_out_of_dbpedia,
                         discard_superclasses=discard_superclasses,
                         instantiation_property=instantiation_property)
        self._target_iris = self._build_target_iris_model(target_iris)

    def _build_target_iris_model(self, raw_target_iris):
        if len(raw_target_iris) < 1 or type(raw_target_iris) == str:
            return raw_target_iris
        return {str(a_raw_iri) for a_raw_iri in raw_target_iris}

    def _decide_relevant_triple_func(self):
        return self._is_a_relevant_triple_dbpedia_filter \
            if self._filter_not_dbpedia \
            else self._is_a_relevant_triple_no_dbpedia_filter

    def _is_relevante_triple_dbpedia_targets(self, a_triple):
        return self._is_a_relevant_triple_no_dbpedia_filter(a_triple) \
               and self._is_a_dbpedia_type(a_triple[O]) \
               and str(a_triple[S]) in self._target_iris

    def _is_relevant_triple_targets_any_namespace(self, a_triple):
        return a_triple[P] == self._instantiation_property \
               and str(a_triple[S]) in self._target_iris


class BackLinkCache(object):

    def __init__(self, source_file, wikilink_property=WIKILINK_PROPERTY):
        self._wikilink_property = wikilink_property \
            if type(wikilink_property) == Property \
            else Property(wikilink_property)
        self._wikilinks_dict = {}
        self._load_wikilink_dict(source_file)

    def get_links_from_entity(self, dbpedia_id):
        if dbpedia_id in self._wikilinks_dict:
            return self._wikilinks_dict[dbpedia_id]
        return None

    def has_a_wikilink(self, source, destination):
        if source not in self._wikilinks_dict:
            return False
        return destination in self._wikilinks_dict[source]

    def _load_wikilink_dict(self, source_file):
        t_yielder = NtTriplesYielder(source_file=source_file,
                                     allow_untyped_numbers=False,
                                     raw_graph=None)
        for a_triple in t_yielder.yield_triples():
            # if self._is_relevant_triple(a_triple):  # doesnt really need to check anything, the files are solid
            #     self._annotate_triple(a_triple)
            self._annotate_triple(a_triple)

    def _is_relevant_triple(self, triple):
        return triple[P] == self._wikilink_property

    def _annotate_triple(self, triple):
        subj_iri = triple[S].iri
        obj_iri = triple[O].iri

        self._add_elem_to_dict_if_needed(subj_iri)

        self._annotate_link(source=subj_iri,
                            destination=obj_iri)

    def _add_elem_to_dict_if_needed(self, an_iri):
        if an_iri not in self._wikilinks_dict:
            self._wikilinks_dict[an_iri] = []

    def _annotate_link(self, source, destination):
        self._wikilinks_dict[source].append(destination)


class DestFilteredBackLinkCache(BackLinkCache):

    def __init__(self, source_file, target_iris):
        self._target_iris = self._build_target_iris_model(target_iris)
        super().__init__(source_file)


    def _build_target_iris_model(self, raw_target_iris):
        if len(raw_target_iris) < 1 or type(raw_target_iris) == str:
            return raw_target_iris
        return {str(a_raw_iri) for a_raw_iri in raw_target_iris}

    def _annotate_triple(self, a_triple):
        if self._is_relevant_triple(a_triple):
            super()._annotate_triple(a_triple)

    def _is_relevant_triple(self, a_triple):
        return str(a_triple[_O]) in self._target_iris

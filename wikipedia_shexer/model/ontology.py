from rdflib import Graph, RDF, OWL, RDFS, URIRef

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

    @property
    def properties_with_domran(self):
        return [a_prop for a_prop in self._object_properties_with_domran]

    def get_properties_matching_domran(self, subject_class, object_class, cache_subj=False, cache_obj=False):
        # TODO implement cache using whatevah
        result = set()
        for a_property in self._object_properties_with_domran:
            target_prop_dict = self._domran_dict[str(a_property)]
            if self._matches_domran(target_prop_dict, subject_class, object_class):
                result.add(str(a_property))
        return list(result)

    def subj_and_obj_class_matches_domran(self, subj_class, obj_class, property):
        if property not in self._object_properties_with_domran:
            return False
        return self._matches_domran(self._domran_dict[property], subj_class, obj_class)

    def has_property_domran(self, property):
        return property in self._domran_dict


    def _matches_domran(self, target_prop_dict, subject_class, object_class):
        if len(target_prop_dict[_DOMAIN_KEY]):
            if len(target_prop_dict[_RANGE_KEY]) > 0:  # CASE DOM + RAN

                return self._matches_domain(target_prop_dict, subject_class) and \
                        self._matches_range(target_prop_dict, object_class)
            else:  # CASE DOM

                return self._matches_domain(target_prop_dict, subject_class)
        else: # CASE RAN. It can't be no DOM and no RAN at this point

            return self._matches_range(target_prop_dict, object_class)



    def _matches_feature(self, prop_dict, candidate_class, key_dict):
        for a_superclass in prop_dict[key_dict]:
            if self._is_superclass(superclass=URIRef(a_superclass),
                                   candidate=URIRef(candidate_class)):
                return True

        return False

    def _is_superclass(self, superclass, candidate):
        if candidate == superclass:
            return True
        for a_triple in self._ontog.triples((URIRef(candidate), RDFS.subClassOf, None)):
            if a_triple[2] == superclass:
                return True
            elif self._is_superclass(superclass=superclass,
                                     candidate=a_triple[2]):
                return True
        return False

    def _matches_range(self, prop_dict, object_class):
        return self._matches_feature(prop_dict=prop_dict,
                                     candidate_class=object_class,
                                     key_dict=_RANGE_KEY)

    def _matches_domain(self, prop_dict, subject_class):
        return self._matches_feature(prop_dict=prop_dict,
                                     candidate_class=subject_class,
                                     key_dict=_DOMAIN_KEY)

    def _get_object_properties(self):
        result = []
        for triple in self._ontog.triples((None, RDF.type, OWL.ObjectProperty)):
            result.append(triple[0])
        return result

    def _init_domrans(self):
        partial_dict = {}
        for a_prop in self._object_poperties:
            str_prop = str(a_prop)
            partial_dict[str_prop] = {_DOMAIN_KEY : set(),
                                      _RANGE_KEY : set()}
            domain = range = False
            for a_triple in self._ontog.triples((a_prop, RDFS.domain, None)):
                partial_dict[str_prop][_DOMAIN_KEY].add(str(a_triple[2]))
                domain = True

            for a_triple in self._ontog.triples((a_prop, RDFS.range, None)):
                partial_dict[str_prop][_RANGE_KEY].add(str(a_triple[2]))
                range = True

            if domain or range:
                self._domran_dict[str_prop] = {_DOMAIN_KEY: partial_dict[str_prop][_DOMAIN_KEY],
                                               _RANGE_KEY: partial_dict[str_prop][_RANGE_KEY]}
                self._object_properties_with_domran.append(a_prop)
        print(self._domran_dict)

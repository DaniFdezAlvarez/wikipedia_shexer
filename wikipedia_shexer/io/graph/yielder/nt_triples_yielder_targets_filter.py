from wikipedia_shexer.io.graph.yielder.nt_triples_yielder import NtTriplesYielder
from wikipedia_shexer.io.graph.yielder.base_triples_yielder import _S, _O


class NtTriplesYielderTargetsFilter(NtTriplesYielder):

    def __init__(self, target_iris, source_file=None, allow_untyped_numbers=False, raw_graph=None):
        super().__init__(source_file=source_file,
                         allow_untyped_numbers=allow_untyped_numbers,
                         raw_graph=raw_graph)
        self._target_iris = target_iris if type(target_iris == set) else set(target_iris)
        self._true_triples = 0

    def yield_triples(self):
        for a_triple in super().yield_triples():
            if self._is_relevant_triple(a_triple):
                yield a_triple
                self._true_triples += 1

    def _is_relevant_triple(self, a_triple):
        return self._is_target_iri(a_triple[_S]) or self._is_target_iri(a_triple[_O])

    def _is_target_iri(self, obj_iri):
        return obj_iri.iri in self._target_iris

    @property
    def yielded_triples(self):
        return self._true_triples

    def _reset_count(self):
        super()._reset_count()
        self._true_triples = 0

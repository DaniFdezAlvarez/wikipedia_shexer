
from wikipedia_shexer.io.graph.yielder.base_triples_yielder import BaseTriplesYielder, _S, _O
from wikipedia_shexer.model.rdf import Iri


class JustIrisTriplesYielder(BaseTriplesYielder):

    def __init__(self, base_yielder):
        super().__init__()
        self._base_yielder = base_yielder

    def yield_triples(self):
        for a_triple in self._base_yielder.yield_triples():
            if type(a_triple[_S]) == Iri and type(a_triple[_O]) == Iri:
                yield a_triple
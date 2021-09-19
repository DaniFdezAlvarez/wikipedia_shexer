from wikipedia_shexer.io.graph.yielder.base_triples_yielder import BaseTriplesYielder, _S, _P, _O

class StrTriplesYielder(BaseTriplesYielder):

    def __init__(self, base_yielder):
        super().__init__()
        self._base_yielder = base_yielder

    def yield_triples(self):
        for a_triple in self._base_yielder.yield_triples():
            yield (str(a_triple[_S]), str(a_triple[_P]), str(a_triple[_O]))

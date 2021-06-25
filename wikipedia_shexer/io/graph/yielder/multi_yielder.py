
from wikipedia_shexer.io.graph.yielder.base_triples_yielder import BaseTriplesYielder

class MultiYielder(BaseTriplesYielder):

    def __init__(self, yielder_list):
        super().__init__()
        self._yielder_list = yielder_list


    def yield_triples(self):
        for a_yielder in self._yielder_list:
            for a_triple in a_yielder.yield_triples():
                yield a_triple

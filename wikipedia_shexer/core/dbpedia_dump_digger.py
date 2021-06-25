from wikipedia_shexer.io.graph.yielder.nt_triples_yielder_targets_filter import NtTriplesYielderTargetsFilterNoLiterals
from wikipedia_shexer.io.graph.yielder.multi_yielder import MultiYielder

_S = 0
_P = 1
_O = 2


class DBpediaDumpDigger(object):

    def __init__(self, source_files):
        self._source_files = source_files
        self._yielder = self._build_yielder(source_files)
        self._root_entities = None  # It will be a dict after executing update_root_entities

    def fill_true_triples_of_model_abstract(self, m_abstract):
        self._update_root_entities([m_abstract])
        self._find_relevant_true_triples()

    def fill_true_triples_of_model_abstracts(self, model_abstracts_list):
        """
        In case you want to get the true triples of several model abstracts, please use
        this method instead of fill_true_triples_of_model_abstract. Both iterate over a local file.
        But this one will iterate a single time for the whole abstracts, while the other one will
        iterate n times for n abstracts.

        :param model_abstracts_list:
        :return:
        """
        self._update_root_entities(model_abstracts_list)
        self._find_relevant_true_triples()

    def _yield_builder(self, source_files):
        if len(source_files) == 1:
            return NtTriplesYielderTargetsFilterNoLiterals(target_iris=self._root_entities,
                                                           source_file=source_files[0])
        return MultiYielder(
            yielder_list=
            [
                NtTriplesYielderTargetsFilterNoLiterals(
                    target_iris=self._root_entities,
                    source_file=a_path
                )
                for a_path in source_files
            ]
        )

    def _find_relevant_true_triples(self):
        self._find_true_triples_in_source()
        self._tear_down()

    def _find_true_triples_in_source(self):
        for a_triple in self._yielder.yield_triples():  # triples are (str, str, str), not any model object
            self._check_subject_candidate_annotation(a_triple)
            self._check_object_candidate_annotation(a_triple)

    def _check_object_candidate_annotation(self, a_triple):
        if a_triple[_O] not in self._root_entities:
            return
        target_abstract = self._root_entities[a_triple[_S]]
        mention_obj = self._look_for_mention_of_triple(abstract=target_abstract,
                                                       a_triple=a_triple,
                                                       mention_pos=_S)
        if mention_obj is None:
            return

        target_abstract.add_inverse_true_triple(mention=mention_obj,
                                                triple=a_triple)

    def _check_subject_candidate_annotation(self, a_triple):
        if a_triple[_S] not in self._root_entities:
            return
        target_abstract = self._root_entities[a_triple[_S]]
        mention_obj = self._look_for_mention_of_triple(abstract=target_abstract,
                                                       a_triple=a_triple,
                                                       mention_pos=_O)
        if mention_obj is None:
            return

        target_abstract.add_direct_true_triple(mention=mention_obj,
                                               triple=a_triple)

    def _look_for_mention_of_triple(self, abstract, a_triple, mention_pos):
        target_mention = a_triple[mention_pos]
        for a_mention in abstract.mentions():
            if a_mention.dbpedia_id == target_mention:
                return a_mention
        return None

    def _tear_down(self):
        self._root_entities = None  # Avoid allocating this in memory when its not necessary

    def _update_root_entities(self, abstract_list):
        """
        It initiaties a dict in self._root entities where keys as dbpedia IDs and values are the actual model objects

        self._root_entities can be used at a time to check the relevance of a triple and to add a true triple to the
        corresponding abstract model object.

        :param abstract_list:
        :return:
        """
        self._root_entities = {an_abstract.dbpedia_id: an_abstract for an_abstract in abstract_list}

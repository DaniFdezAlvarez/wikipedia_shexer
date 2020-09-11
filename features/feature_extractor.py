from wikipedia_shexer.model.consts import S, O
from wikipedia_shexer.utils.dbpedia_utils import DBpediaUtils

class FeatureExtractor(object):

    def __init__(self, ontology):
        self._ontology = ontology


    def rows_from_abstract(self, abstract):
        target_types = DBpediaUtils.get_types_of_a_dbpedia_node(dbp_node=abstract.dbpedia_id)
        positive_rows = self._extract_positive_rows()
        negative_rows = self._extacrt_negative_rows()


    def _extract_positive_rows(self):
        # Get type(s) of target page.
        # Then, 1 by 1, types of mentions with true triples
        # Try to build a damm obj. But we will need to get candidates, not just relative positional numbers
        pass # TODO

    def _extract_negative_rows(self):
        pass # TODO


    # props_d = self._ontology.get_properties_matching_domran(subject_class=a_true_triple[S],
    #                                                         object_class=a_true_triple[O],
    #                                                         cache_subj=True,
    #                                                         cache_obj=False)



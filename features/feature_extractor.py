from wikipedia_shexer.model.consts import S, P, O
from wikipedia_shexer.model.feature import Row
from wikipedia_shexer.utils.dbpedia_utils import DBpediaUtils


class FeatureExtractor(object):

    def __init__(self, ontology):
        self._ontology = ontology

    def rows_from_abstract(self, abstract):
        result = []
        target_types = DBpediaUtils.get_types_of_a_dbpedia_node(dbp_node=abstract.dbpedia_id)
        for a_sentence in abstract.sentences():
            for a_mention in a_sentence.mentions():
                result += self._extract_rows_direct_triples(abstract=abstract,
                                                            sentence=a_sentence,
                                                            mention=a_mention,
                                                            target_types=target_types)
                result += self._extract_rows_inverse_triples(abstract=abstract,
                                                             sentence=a_sentence,
                                                             mention=a_mention,
                                                             target_types=target_types)

    def _extract_rows_direct_triples(self, abstract, sentence, mention, target_types):
        # TODO -->
        # 1 - REFACTOR
        # 2 - DO THE SAME WITH INVERSE TRIPLES
        # 3 - BUILD AND MANAGE CANDIDATES DICT
        result = []
        true_property = mention.true_triple[P] \
            if mention.has_triple and mention.true_triple[S] == abstract.dbpedia_id \
            else None
        if mention.has_triple and mention.true_triple[S] == abstract.dbpedia_id:
            result.append(Row(positive=True,
                              property=true_property,
                              n_candidates_in_abstract="",  # TODO
                              n_candidates_in_sentence="",  # TODO
                              rel_position_sentence_in_abstract=sentence.abstract_relative_position,
                              rel_position_vs_candidates_in_sentence="",  # TODO
                              rel_position_vs_candidates_in_abstract="",  # TODO
                              n_entities_in_sentence=sentence.n_mentions,
                              rel_position_vs_entities_in_abstract=mention.abstract_relative_position,
                              rel_position_vs_entities_in_sentence=mention.sentence_relative_position,
                              back_link="",  # TODO
                              ))
        mention_types = DBpediaUtils.get_types_of_a_dbpedia_node(mention.dbpedia_id)
        for t_target, t_mention in FeatureExtractor._type_combinations(target_types, mention_types):
            for a_property in self._ontology.get_properties_matching_domran(subject_class=t_target,
                                                                            object_class=t_mention,
                                                                            cache_subj=True,
                                                                            cache_obj=False):
                if a_property != true_property:
                    result.append(Row(positive=False,
                                      property=a_property,
                                      n_candidates_in_abstract="",  # TODO
                                      n_candidates_in_sentence="",  # TODO
                                      rel_position_sentence_in_abstract=sentence.abstract_relative_position,
                                      rel_position_vs_candidates_in_sentence="",  # TODO
                                      rel_position_vs_candidates_in_abstract="",  # TODO
                                      n_entities_in_sentence=sentence.n_mentions,
                                      rel_position_vs_entities_in_abstract=mention.abstract_relative_position,
                                      rel_position_vs_entities_in_sentence=mention.sentence_relative_position,
                                      back_link="",  # TODO
                                      ))
        return result

    @staticmethod
    def _type_combinations(list_types_1, list_types_2):
        for at1 in list_types_1:
            for at2 in list_types_2:
                yield ((at1, at2))

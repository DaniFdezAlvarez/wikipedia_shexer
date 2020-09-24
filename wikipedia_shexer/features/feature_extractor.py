from wikipedia_shexer.model.consts import S, P
from wikipedia_shexer.model.feature import Row
from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import dbpedia_id_to_page_title
from wikipedia_shexer.features.feature_serialization import CSVRowSerializator

_KEY_DIRECT = "D"
_KEY_INVERSE = "I"


class FeatureExtractor(object):

    def __init__(self, ontology, type_cache, backlink_cache):
        self._ontology = ontology
        self._type_cache = type_cache
        self._backlink_cache = backlink_cache

    def rows_from_abstract(self, abstract):
        result = []
        types_of_target = self._type_cache.get_types_of_node(node=abstract.dbpedia_id)
        property_sense_tuples = self._find_properties_sense_tuples(abstract=abstract,
                                                                   target_entity=abstract.dbpedia_id)

        candidates_dict = self._build_candidates_dict(abstract=abstract,
                                                      target_types=types_of_target,
                                                      property_sense_tuples=property_sense_tuples)  # DONE

        for a_sentence in abstract.sentences():  # Sounds fancy
            for a_mention in a_sentence.mentions():
                if a_mention.has_triple:
                    if a_mention.true_triple[S] == abstract.dbpedia_id:
                        result += self._extract_rows_direct_triples(abstract=abstract,
                                                                    sentence=a_sentence,
                                                                    mention=a_mention,
                                                                    target_types=types_of_target,
                                                                    candidates_dict=candidates_dict)
                    else:
                        result += self._extract_rows_inverse_triples(abstract=abstract,
                                                                     sentence=a_sentence,
                                                                     mention=a_mention,
                                                                     target_types=types_of_target,
                                                                     candidates_dict=candidates_dict)
        return result

    def serialize_rows(self, rows, file_path=None, str_return=False):
        if not str_return and file_path is None:
            raise ValueError("You must set to Tro str return or to specify a valid file path to serialize thw rows")
        serializator = CSVRowSerializator()
        if str_return:
            return "\n".join(a_row for a_row in serializator.serialize_rows(rows))
        else:
            self._write_rows_to_file(rows=rows, file_path=file_path, serializator=serializator)

    def _find_properties_sense_tuples(self, abstract, target_entity):
        result = []
        for a_triple in abstract.true_triples():
            result.append((a_triple[P],
                           _KEY_DIRECT if a_triple[S] == target_entity else _KEY_INVERSE))
        return result

    def _write_rows_to_file(self, rows, file_path, serializator):
        with open(file_path, "w") as out_stream:
            for a_row in serializator.serialize_rows(rows):
                out_stream.write(a_row + "\n")

    def _build_candidates_dict(self, abstract, target_types, property_sense_tuples):
        result = {_KEY_DIRECT: {},
                  _KEY_INVERSE: {}}
        for a_tuple in property_sense_tuples:
            if a_tuple[1] == _KEY_DIRECT:
                self._fill_candidate_dict_with_sense_prop(abstract=abstract,
                                                          target_types=target_types,
                                                          prop=a_tuple[0],
                                                          candidate_dict=result,
                                                          direct=True)
            else:
                self._fill_candidate_dict_with_sense_prop(abstract=abstract,
                                                          target_types=target_types,
                                                          prop=a_tuple[0],
                                                          candidate_dict=result,
                                                          direct=False
                                                          )
        return result

    def _fill_candidate_dict_with_sense_prop(self, abstract, target_types, prop, candidate_dict, direct):
        target_result_key = _KEY_DIRECT if direct else _KEY_INVERSE
        for a_sentence in abstract.sentences:
            for a_mention in a_sentence.mentions:
                mention_types = self._type_cache.get_types_of_node(node=a_mention.dbpedia_id)
                for t_target, t_mention in FeatureExtractor._type_combinations(target_types, mention_types):
                    if self._ontology.subj_and_obj_class_matches_domran(subj_class=t_target if direct else t_mention,
                                                                        obj_class=t_mention if direct else t_target,
                                                                        a_property=prop):
                        if prop not in candidate_dict[target_result_key]:
                            candidate_dict[target_result_key] = {}

                        if a_sentence.relative_position not in candidate_dict[target_result_key][prop]:
                            candidate_dict[target_result_key][prop][a_sentence.relative_position] = []
                        candidate_dict[target_result_key][prop][a_sentence.relative_position].append(
                            a_mention)

        # print("vaya tela con tu wela")
        # self._fill_sense_of_candidates_dict(result=result,
        #                                     abstract=abstract,
        #                                     target_types=target_types,
        #                                     direct=True)
        # print("Vaya cisco aquí en la disco")
        # self._fill_sense_of_candidates_dict(result=result,
        #                                     abstract=abstract,
        #                                     target_types=target_types,
        #                                     direct=False)
        # print("Vaya timo con tu primo")
        # return result
    #
    # def _fill_sense_of_candidates_dict(self, result, abstract, target_types, direct):
    #     target_result_key = _KEY_DIRECT if direct else _KEY_INVERSE
    #     for a_sentence in abstract.sentences():
    #         for a_mention in a_sentence.mentions():
    #             mention_types = self._type_cache.get_types_of_node(node=a_mention.dbpedia_id)
    #             for t_target, t_mention in FeatureExtractor._type_combinations(target_types, mention_types):
    #                 for a_property in \
    #                         self._ontology.get_properties_matching_domran(
    #                             subject_class=t_target if direct else t_mention,
    #                             object_class=t_mention if direct else t_target,
    #                             cache_subj=True if direct else False,
    #                             cache_obj=False if direct else True
    #                         ):
    #                     if a_property not in result[target_result_key]:
    #                         result[target_result_key][a_property] = {}
    #                     if a_sentence.relative_position not in result[target_result_key][a_property]:
    #                         result[target_result_key][a_property][a_sentence.relative_position] = []
    #                     result[target_result_key][a_property][a_sentence.relative_position].append(
    #                         a_mention.sentence_relative_position)

    def _extract_rows_direct_triples(self, abstract, sentence, mention, target_types, candidates_dict):
        return self._extract_rows_triples_for_a_sense(abstract=abstract,
                                                      sentence=sentence,
                                                      mention=mention,
                                                      target_types=target_types,
                                                      candidates_dict=candidates_dict,
                                                      direct=True)

    def _extract_rows_inverse_triples(self, abstract, sentence, mention, target_types, candidates_dict):
        return self._extract_rows_triples_for_a_sense(abstract=abstract,
                                                      sentence=sentence,
                                                      mention=mention,
                                                      target_types=target_types,
                                                      candidates_dict=candidates_dict,
                                                      direct=False)

    def _extract_rows_triples_for_a_sense(self, abstract, sentence, mention, target_types, candidates_dict, direct):
        result = []
        page_id = dbpedia_id_to_page_title(abstract.dbpedia_id)
        target_key_result = _KEY_DIRECT if direct else _KEY_INVERSE
        true_property = mention.true_triple[P]
        result.append(self._build_row(page_id=page_id,
                                      positive=True,
                                      prop=true_property,
                                      sentence=sentence,
                                      mention=mention,
                                      candidates_dict=candidates_dict,
                                      direct=direct))
        # [target_result_key][a_property][a_sentence.relative_position]
        for a_sentence_position in candidates_dict[target_key_result][true_property]:
            a_wrong_sentence = abstract.get_sentence_by_pos(a_sentence_position)
            for a_wrong_mention in candidates_dict[target_key_result][true_property][a_sentence_position]:
                if a_wrong_mention != mention:
                    result.append(self._build_row(page_id=page_id,
                                                  positive=False,
                                                  prop=true_property,
                                                  sentence=a_wrong_sentence,
                                                  mention=a_wrong_mention,
                                                  candidates_dict=candidates_dict,
                                                  direct=direct))


        # true_property = mention.true_triple[P] \
        #     if mention.has_triple and mention.true_triple[POS_TARGET] == abstract.dbpedia_id \
        #     else None
        # if mention.has_triple and mention.true_triple[POS_TARGET] == abstract.dbpedia_id:
        #     result.append(self._build_row(page_id=page_id,
        #                                   positive=True,
        #                                   prop=true_property,
        #                                   sentence=sentence,
        #                                   mention=mention,
        #                                   candidates_dict=candidates_dict,
        #                                   direct=direct))
        # mention_types = self._type_cache.get_types_of_node(node=mention.dbpedia_id)
        # for t_target, t_mention in FeatureExtractor._type_combinations(target_types, mention_types):
        #     print(t_target, t_mention)
        #     for a_property in self._ontology.get_properties_matching_domran(
        #             subject_class=t_target if direct else t_mention,
        #             object_class=t_mention if direct else t_target,
        #             cache_subj=True if direct else False,
        #             cache_obj=False if direct else True):
        #         if a_property != true_property:
        #             result.append(self._build_row(page_id=page_id,
        #                                           positive=False,
        #
        #                                           prop=a_property,
        #                                           sentence=sentence,
        #                                           mention=mention,
        #                                           candidates_dict=candidates_dict,
        #                                           direct=direct))
        # return result

    def _build_row(self, page_id, positive, prop, sentence, mention, candidates_dict, direct):
        target_sense_key = _KEY_DIRECT if direct else _KEY_INVERSE
        return Row(positive=positive,
                   prop=prop,
                   instance=page_id,
                   mention=mention.entity_id,
                   direct=direct,
                   n_candidates_in_abstract=self._count_candidates_in_abstract(prop=prop,
                                                                               candidates_dict=candidates_dict,
                                                                               sense_key=target_sense_key),
                   n_candidates_in_sentence=self._count_candidates_in_sentece(prop=prop,
                                                                              sentence=sentence,
                                                                              candidates_dict=candidates_dict,
                                                                              sense_key=target_sense_key),
                   rel_position_sentence_in_abstract=sentence.abstract_relative_position,
                   rel_position_vs_candidates_in_sentence=self._relative_position_in_sentence(prop=prop,
                                                                                              sentence=sentence,
                                                                                              mention=mention,
                                                                                              candidates_dict=candidates_dict,
                                                                                              sense_key=target_sense_key),
                   rel_position_vs_candidates_in_abstract=self._relative_position_in_abstract(prop=prop,
                                                                                              sentence=sentence,
                                                                                              mention=mention,
                                                                                              candidates_dict=candidates_dict,
                                                                                              sense_key=target_sense_key),
                   n_entities_in_sentence=sentence.n_mentions,
                   rel_position_vs_entities_in_abstract=mention.abstract_relative_position,
                   rel_position_vs_entities_in_sentence=mention.sentence_relative_position,
                   back_link=self._backlink_cache.has_a_wikilink(source=mention.dbpedia_id,
                                                                 destination=page_id)  # TODO looks like this in
                   # TODO the paper, but ensure it
                   )

    @staticmethod
    def _relative_position_in_abstract(prop, sentence, mention, candidates_dict, sense_key):
        base_result = FeatureExtractor._relative_position_in_sentence(prop, sentence, mention, candidates_dict,
                                                                      sense_key)
        indexes_sentences_with_candidates = [sentence_index for sentence_index
                                             in candidates_dict[sense_key][prop]
                                             if sentence_index < sentence.relative_position]
        for an_index in indexes_sentences_with_candidates:
            base_result += len(candidates_dict[sense_key][prop][an_index])
        return base_result

    @staticmethod
    def _relative_position_in_sentence(prop, sentence, mention, candidates_dict, sense_key):
        target_list_of_mentions = candidates_dict[sense_key][prop][sentence.relative_position]
        return target_list_of_mentions.index(mention)

    @staticmethod
    def _count_candidates_in_abstract(prop, candidates_dict, sense_key):
        result = 0
        for candidates_in_sentence in candidates_dict[sense_key][prop].values():
            result += len(candidates_in_sentence)
        return result

    @staticmethod
    def _count_candidates_in_sentece(prop, sentence, candidates_dict, sense_key):
        return len(candidates_dict[sense_key][prop][sentence.relative_position])

    @staticmethod
    def _type_combinations(list_types_1, list_types_2):
        for at1 in list_types_1:
            for at2 in list_types_2:
                yield ((at1, at2))

from wikipedia_shexer.model.consts import S, P, O
from wikipedia_shexer.model.feature import Row
from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import dbpedia_id_to_page_title
from wikipedia_shexer.features.feature_serialization import CSVRowSerializator
from wikipedia_shexer.utils.wikipedia_utils import WikipediaUtils
import time

_KEY_DIRECT = "D"
_KEY_INVERSE = "I"


class FeatureExtractor(object):

    def __init__(self, ontology, type_cache, backlink_cache):
        self._ontology = ontology
        self._type_cache = type_cache
        self._backlink_cache = backlink_cache

    def rows_to_file_from_page_list(self, page_list, inverse, file_path):
        serializator = CSVRowSerializator()
        with open(file_path, "w") as out_stream:
            for a_page in page_list:
                init = time.time()
                print("------------ Init", a_page)
                try:
                    rows = self.rows_from_abstract(WikipediaUtils.extract_model_abstract(page_id=a_page,
                                                                                         inverse=inverse))
                    for a_serialized_row in serializator.serialize_rows(rows):
                        out_stream.write(a_serialized_row + "\n")
                    print("Finished", a_page, str(time.time() - init))
                except BaseException as e:
                    print("---- ABORTED ----", a_page, str(time.time() - init))
                    print(e)

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
        # target_result_key = _KEY_DIRECT if direct else _KEY_INVERSE
        for a_sentence in abstract.sentences():
            for a_mention in a_sentence.mentions():
                self._annotate_mention_in_candidates_dict_if_needed(instance=abstract.dbpedia_id,
                                                                    sentence=a_sentence,
                                                                    mention=a_mention,
                                                                    target_types=target_types,
                                                                    prop=prop,
                                                                    candidates_dict=candidate_dict,
                                                                    direct=direct)

    def _annotate_mention_in_candidates_dict_if_needed(self, instance, sentence, mention, target_types,
                                                       prop, candidates_dict, direct):
        target_result_key = _KEY_DIRECT if direct else _KEY_INVERSE
        true_candidate=False
        added=False
        if self._contains_a_matching_true_triple(mention=mention,
                                                 prop=prop,
                                                 instance=instance,
                                                 direct=direct):  # Then no need to check domran, add it
            # self._add_entry_to_candidates_dict(prop=prop,
            #                                    target_key=target_result_key,
            #                                    candidates_dict=candidates_dict,
            #                                    sentence_pos=sentence.relative_position,
            #                                    mention=mention)
            print("Such a sucess!", mention.dbpedia_id, prop, direct)
            true_candidate=True
            # return
        mention_types = self._type_cache.get_types_of_node(node=mention.dbpedia_id)
        for t_target, t_mention in FeatureExtractor._type_combinations(target_types, mention_types):
            if self._ontology.subj_and_obj_class_matches_domran(subj_class=t_target if direct else t_mention,
                                                                obj_class=t_mention if direct else t_target,
                                                                a_property=prop):
                self._add_entry_to_candidates_dict(prop=prop,
                                                   target_key=target_result_key,
                                                   candidates_dict=candidates_dict,
                                                   sentence_pos=sentence.relative_position,
                                                   mention=mention)
                print("CANDIDATE!", mention.dbpedia_id, prop, direct)
                added=True
                break
        if true_candidate and not added:
            print("DEMOLISIONNNNNNN", mention.dbpedia_id, prop, direct, sentence.text)




    def _contains_a_matching_true_triple(self, mention, prop, instance, direct):
        return mention.has_triple and \
               mention.true_triple[P] == prop and \
               mention.true_triple[S if direct else O] == instance

    def _add_entry_to_candidates_dict(self, prop, target_key, candidates_dict, sentence_pos, mention):
        if prop not in candidates_dict[target_key]:
            candidates_dict[target_key] = {}
        if sentence_pos not in candidates_dict[target_key][prop]:
            candidates_dict[target_key][prop][sentence_pos] = []
        candidates_dict[target_key][prop][sentence_pos].append(mention)


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
            a_wrong_sentence = abstract.get_sentence_by_position(a_sentence_position)
            for a_wrong_mention in candidates_dict[target_key_result][true_property][a_sentence_position]:
                if a_wrong_mention != mention:
                    result.append(self._build_row(page_id=page_id,
                                                  positive=False,
                                                  prop=true_property,
                                                  sentence=a_wrong_sentence,
                                                  mention=a_wrong_mention,
                                                  candidates_dict=candidates_dict,
                                                  direct=direct))
        return result

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
                                                                 destination=page_id)
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

from wikipedia_shexer.model.consts import S, P, O
from wikipedia_shexer.model.feature import Row
from wikipedia_shexer.utils.dbpedia_utils import DBpediaUtils
from wikipedia_shexer.utils.wikipedia_utils import WikipediaUtils
from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import dbpedia_id_to_page_title
from wikipedia_shexer.features.feature_serialization import CSVRowSerializator



_KEY_DIRECT = "D"
_KEY_INVERSE = "I"


class FeatureExtractor(object):

    def __init__(self, ontology):
        self._ontology = ontology

    def rows_from_abstract(self, abstract):
        result = []
        target_types = DBpediaUtils.get_types_of_a_dbpedia_node(dbp_node=abstract.dbpedia_id)
        print("Que fino tu pepino?")
        candidates_dict = self._build_candidates_dict(abstract=abstract,
                                                      target_types=target_types)
        print("Que pacha por tu cacha?")
        for a_sentence in abstract.sentences():
            for a_mention in a_sentence.mentions():
                print("Made one", a_mention.dbpedia_id)
                result += self._extract_rows_direct_triples(abstract=abstract,
                                                            sentence=a_sentence,
                                                            mention=a_mention,
                                                            target_types=target_types,
                                                            candidates_dict=candidates_dict)
                result += self._extract_rows_inverse_triples(abstract=abstract,
                                                             sentence=a_sentence,
                                                             mention=a_mention,
                                                             target_types=target_types,
                                                             candidates_dict=candidates_dict)
        return result

    def serialize_rows(self, rows, file_path=None, str_return=False):
        if not str_return and file_path is None:
            raise ValueError("You must set to Tro str return or to specify a valid file path to serialize thw rows")
        all_properties = self._ontology.properties_with_domran
        serializator = CSVRowSerializator(all_properties=all_properties)
        if str_return:
            return "\n".join(a_row for a_row in serializator.serialize_rows(rows))
        else:
            self._write_rows_to_file(rows=rows, file_path=file_path, serializator=serializator)


    def _write_rows_to_file(self, rows, file_path, serializator):
        with open(file_path, "w") as out_stream:
            for a_row in serializator.serialize_rows(rows):
                out_stream.write(a_row+"\n")


    def _build_candidates_dict(self, abstract, target_types):
        result = { _KEY_DIRECT : {},
                   _KEY_INVERSE : {}}
        print("vaya tela con tu wela")
        self._fill_sense_of_candidates_dict(result=result,
                                            abstract=abstract,
                                            target_types=target_types,
                                            direct=True)
        print("Vaya cisco aquí en la disco")
        self._fill_sense_of_candidates_dict(result=result,
                                            abstract=abstract,
                                            target_types=target_types,
                                            direct=False)
        print("Vaya timo con tu primo")
        return result

    def _fill_sense_of_candidates_dict(self, result, abstract, target_types, direct):
        target_result_key = _KEY_DIRECT if direct else _KEY_INVERSE
        for a_sentence in abstract.sentences():
            for a_mention in a_sentence.mentions():
                mention_types = DBpediaUtils.get_types_of_a_dbpedia_node(a_mention.dbpedia_id)
                for t_target, t_mention in FeatureExtractor._type_combinations(target_types, mention_types):
                    for a_property in \
                            self._ontology.get_properties_matching_domran(
                                subject_class=t_target if direct else t_mention,
                                object_class=t_mention if direct else t_target,
                                cache_subj=True if direct else False,
                                cache_obj=False if direct else True
                            ):
                        if a_property not in result[target_result_key]:
                            result[target_result_key][a_property] = {}
                        if a_sentence.relative_position not in result[target_result_key][a_property]:
                            result[target_result_key][a_property][a_sentence.relative_position] = []
                        result[target_result_key][a_property][a_sentence.relative_position].append(
                            a_mention.sentence_relative_position)

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
        POS_TARGET = S if direct else O
        true_property = mention.true_triple[P] \
            if mention.has_triple and mention.true_triple[POS_TARGET] == abstract.dbpedia_id \
            else None
        if mention.has_triple and mention.true_triple[POS_TARGET] == abstract.dbpedia_id:
            result.append(self._build_row(page_id=page_id,
                                          positive=True,
                                          prop=true_property,
                                          sentence=sentence,
                                          mention=mention,
                                          candidates_dict=candidates_dict,
                                          direct=direct))
        mention_types = DBpediaUtils.get_types_of_a_dbpedia_node(mention.dbpedia_id)
        for t_target, t_mention in FeatureExtractor._type_combinations(target_types, mention_types):
            print(t_target, t_mention)
            for a_property in self._ontology.get_properties_matching_domran(subject_class=t_target if direct else t_mention,
                                                                            object_class=t_mention if direct else t_target,
                                                                            cache_subj=True if direct else False,
                                                                            cache_obj=False if direct else True):
                print("Oye, mira", a_property)
                if a_property != true_property:
                    result.append(self._build_row(page_id=page_id,
                                                  positive=False,
                                                  prop=a_property,
                                                  sentence=sentence,
                                                  mention=mention,
                                                  candidates_dict=candidates_dict,
                                                  direct=direct))
        return result

    def _build_row(self, page_id, positive, prop, sentence, mention, candidates_dict, direct):
        target_sense_key = _KEY_DIRECT if direct else _KEY_INVERSE
        return Row(positive=positive,
                   prop=prop,
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
                   back_link=WikipediaUtils.has_mention_a_back_link(page_id=page_id,
                                                                    page_mention=dbpedia_id_to_page_title(mention.dbpedia_id),
                                                                    just_summary=False)  # TODO looks like this in
                   # TODO the paper, but ensure it
                   )

    @staticmethod
    def _relative_position_in_abstract(prop, sentence, mention, candidates_dict, sense_key):
        base_result = FeatureExtractor._relative_position_in_sentence(prop, sentence, mention, candidates_dict, sense_key)
        indexes_sentences_with_candidates = [sentence_index for sentence_index
                                             in candidates_dict[sense_key][prop]
                                             if sentence_index < sentence.relative_position]
        for an_index in indexes_sentences_with_candidates:
            base_result += len(candidates_dict[sense_key][prop][an_index])
        return base_result


    @staticmethod
    def _relative_position_in_sentence(prop, sentence, mention, candidates_dict, sense_key):
        target_list_of_mentions = candidates_dict[sense_key][prop][sentence.relative_position]
        return target_list_of_mentions.index(mention.sentence_relative_position)


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
        print("eeh")
        print(list_types_1)
        print(list_types_2)
        for at1 in list_types_1:
            for at2 in list_types_2:
                yield ((at1, at2))

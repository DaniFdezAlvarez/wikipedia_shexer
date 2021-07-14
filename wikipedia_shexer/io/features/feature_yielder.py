from wikipedia_shexer.io.line_reader.file_line_reader import FileLineReader
from wikipedia_shexer.model.feature import Row
from wikipedia_shexer.io.features.const import *


class FeatureYielder(object):

    def __init__(self, rows_path, separator=";"):
        self._rows_path = rows_path
        self._serapator = separator

    def yield_rows(self):
        for a_line in FileLineReader(source_file=self._rows_path,
                                     skip_first_line=True).read_lines():
            pieces = a_line.split(self._serapator)
            yield Row(prop=pieces[PROPERTY_POS],
                      positive=pieces[POSITIVE_POS],
                      back_link=pieces[BACK_LINK_POS],
                      mention=pieces[MENTION_POS],
                      instance=pieces[INSTANCE_POS],
                      n_candidates_in_abstract=pieces[N_CANDIDATES_ABSTRACT_POS],
                      n_candidates_in_sentence=pieces[N_CANDIDATES_SENTENCE_POS],
                      n_entities_in_sentence=pieces[N_ENTITIES_SENTENCE_POS],
                      rel_position_vs_entities_in_abstract=pieces[REL_POS_ENTITIES_ABSTRACT_POS],
                      rel_position_vs_entities_in_sentence=pieces[REL_POS_ENTITIES_SENTENCE_POS],
                      rel_position_vs_candidates_in_abstract=pieces[REL_POS_CANDIDATES_ABSTRACT_POS],
                      rel_position_vs_candidates_in_sentence=pieces[REL_POS_CANDIDATES_SENTENCE_POS],
                      rel_position_sentence_in_abstract=pieces[REL_POS_SENTENCE_ABSTRACT],
                      direct=pieces[DIRECT_POS]
                      )



class CSVRowSerializator(object):

    def __init__(self, all_properties, separator=";"):
        self._separator = separator
        self._all_properties = all_properties


    def serialize_rows(self, rows):
        for a_row in rows:
            yield self.serialize_row(a_row)

    def serialize_row(self, row):
        return self._serialize_row_basic_data(row) + self._serialize_properties(row)


    def _serialize_row_basic_data(self, row):
        return self._separator.join([
            str(row.n_candidates_in_abstract),
            str(row.n_candidates_in_sentence),
            str(row.rel_position_vs_candidates_in_abstract),
            str(row.rel_position_vs_candidates_in_sentence),
            str(row.n_entities_in_sentence),
            str(row.rel_position_vs_entities_in_abstract),
            str(row.rel_position_vs_entities_in_sentence),
            str(row.rel_position_sentence_in_abstract),
            str(row.back_link)
        ])

    def _serialize_properties(self, row, starting_separator=True):
        result = self._separator if starting_separator else ""
        return result + self._separator.join([str(row.prop == a_property) for a_property in self._all_properties])
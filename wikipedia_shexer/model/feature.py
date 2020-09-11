
class Row(object):

    def __init__(self, positive, property,
                 n_candidates_in_abstract,
                 n_candidates_in_sentence,
                 rel_position_vs_candidates_in_abstract,
                 rel_position_vs_candidates_in_sentence,
                 rel_position_sentence_in_abstract,
                 n_entities_in_sentence,
                 rel_position_vs_entities_in_abstract,
                 rel_position_vs_entities_in_sentence,
                 back_link):
        self._positive = positive
        self._property = property
        self._n_candidates_in_abstract = n_candidates_in_abstract
        self._n_candidates_in_sentence = n_candidates_in_sentence
        self._rel_position_vs_candidates_in_abstract = rel_position_vs_candidates_in_abstract
        self._rel_position_vs_candidates_in_sentence = rel_position_vs_candidates_in_sentence
        self._rel_position_sentence_in_abstract = rel_position_sentence_in_abstract
        self._n_entities_in_sentence = n_entities_in_sentence
        self._rel_position_vs_entities_in_abstract = rel_position_vs_entities_in_abstract
        self._rel_position_vs_entities_in_sentence = rel_position_vs_entities_in_sentence
        self._back_link = back_link
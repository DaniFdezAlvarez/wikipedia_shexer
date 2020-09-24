
class Row(object):

    def __init__(self, positive,
                 prop,
                 instance,
                 mention,
                 direct,
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
        self._prop = prop
        self._instance = instance
        self._mention = mention
        self._direct = direct
        self._n_candidates_in_abstract = n_candidates_in_abstract
        self._n_candidates_in_sentence = n_candidates_in_sentence
        self._rel_position_vs_candidates_in_abstract = rel_position_vs_candidates_in_abstract
        self._rel_position_vs_candidates_in_sentence = rel_position_vs_candidates_in_sentence
        self._rel_position_sentence_in_abstract = rel_position_sentence_in_abstract
        self._n_entities_in_sentence = n_entities_in_sentence
        self._rel_position_vs_entities_in_abstract = rel_position_vs_entities_in_abstract
        self._rel_position_vs_entities_in_sentence = rel_position_vs_entities_in_sentence
        self._back_link = back_link


    @property
    def positive(self):
        return self._positive

    @property
    def instance(self):
        return self._instance

    @property
    def mention(self):
        return self._mention

    @property
    def direct(self):
        return self._direct

    @property
    def n_candidates_in_abstract(self):
        return self._n_candidates_in_abstract

    @property
    def n_candidates_in_sentence(self):
        return self._n_candidates_in_sentence

    @property
    def rel_position_vs_candidates_in_abstract(self):
        return self._rel_position_vs_candidates_in_abstract

    @property
    def rel_position_vs_candidates_in_sentence(self):
        return self._rel_position_vs_candidates_in_sentence

    @property
    def rel_position_sentence_in_abstract(self):
        return self._rel_position_sentence_in_abstract

    @property
    def n_entities_in_sentence(self):
        return self._n_entities_in_sentence

    @property
    def rel_position_vs_entities_in_abstract(self):
        return self._rel_position_vs_entities_in_abstract

    @property
    def rel_position_vs_entities_in_sentence(self):
        return self._rel_position_vs_entities_in_sentence

    @property
    def back_link(self):
        return self._back_link

    @property
    def prop(self):
        return self._prop





from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import page_id_to_DBpedia_id
from wikipedia_shexer.model.consts import S, O

class Abstract (object):

    def __init__(self, page_id, sentences=None, text=None, true_direct_mentions=None, true_inverse_mentions=None):
        self._page_id = page_id
        self._dbpedia_id = page_id_to_DBpedia_id(page_id)
        self._sentences = sentences if sentences is not None else []
        self._text = text
        self._true_direct_mentions = true_direct_mentions if true_direct_mentions is not None else []
        self._true_inverse_mentions = true_inverse_mentions if true_inverse_mentions is not None else []
        self._n_mentions = -1

    def fill_internal_numerics_values(self):
        """
        Call this method once the abstract already has been filled with its sentence and mentions objects
        :return:
        """
        self._n_mentions = 0
        for i in range(0, len(self._sentences)):
            target_sentence = self._sentences[i]
            self._n_mentions += target_sentence.n_entities
            for j in range(0, len(self._sentences[i].mentions)):
                target_sentence._mentions[j].relative_position = j + 1
                target_sentence._mentions[j].sentence_relative_position = i + j

    def add_direct_true_triple(self, mention, triple):
        self._true_direct_mentions.append(mention)
        mention.true_triple = triple

    def add_inverse_true_triple(self, mention, triple):
        self._true_inverse_mentions.append(mention)
        mention.true_triple = triple

    def add_sentence(self, sentence):
        self._sentences.append(sentence)

    def true_triples(self):
        for a_mention in self._true_direct_mentions:
            yield a_mention.true_triple
        for a_mention in self._true_inverse_mentions:
            yield a_mention.true_triple

    def direct_true_mentions(self):
        for a_mention in self._true_direct_mentions:
            yield a_mention

    def inverse_true_mentions(self):
        for a_mention in self._true_inverse_mentions:
            yield a_mention

    def sentences(self):
        for a_sentence in self._sentences:
            yield a_sentence

    def mentions(self):
        for a_sentence in self._sentences:
            for a_mention in a_sentence.mentions():
                yield a_mention

    @property
    def text(self):
        return self._text

    @property
    def page_id(self):
        return self._page_id

    @property
    def dbpedia_id(self):
        return self._dbpedia_id

    @property
    def n_mentions(self):
        # WARNING: POTENTIAL INCONSISTENCY. We assume that the abstract wont change once
        # fill_internal_relative_positions_and_numbers is called. Not assuming this implies
        # to explore the whole list of sentences each time to get this number
        return self._n_mentions


class Sentence (object):
    def __init__(self, mentions=None, text=None):
        self._mentions = mentions if mentions is not None else []
        self._text = text

    def add_mention(self, mention):
        self._mentions.append(mention)

    def mentions(self):
        for a_mention in self._mentions:
            yield a_mention

    @property
    def text(self):
        return self._text

    @property
    def n_mentions(self):
        return len(self._mentions)


class Mention(object):
    def __init__(self, entity_id, text=None, relative_position=-1, sentence_relative_position=-1, true_triple=None):
        self._entity_id = entity_id
        self._text = text
        self._relative_position = relative_position
        self._sentence_relative_position = sentence_relative_position
        self._true_triple = None

    @property
    def has_triple(self):
        return self._true_triple is not None

    @property
    def true_triple(self):
        return self._true_triple

    @true_triple.setter
    def true_triple(self, true_triple):
        self._true_triple = true_triple

    @property
    def sentence_relative_position(self):
        return self._sentence_relative_position

    @property
    def relative_position(self):
        return self._relative_position

    @relative_position.setter
    def relative_position(self, pos):
        self._relative_position = pos

    @sentence_relative_position.setter
    def sentence_relative_position(self, sentence_relative_position):
        self._sentence_relative_position = sentence_relative_position

    @property
    def entity_id(self):
        return self._entity_id

    @property
    def text(self):
        return self._text

    @property
    def dbpedia_id(self):
        # it does not need to be stored, better safe memory, it wont be used frequently # TODO sure?
        return page_id_to_DBpedia_id(self._entity_id)

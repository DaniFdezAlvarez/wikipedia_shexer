from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import page_id_to_DBpedia_id

class Abstract (object):

    def __init__(self, page_id, sentences=None, text=None, true_triples=None):
        self._page_id = page_id
        self._sentences = sentences if sentences is not None else []
        self._text = text
        self._true_triples = true_triples if true_triples is not None else []

    def add_sentence(self, sentence):
        self._sentences.append(sentence)

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


class Mention(object):
    def __init__(self, entity_id, text=None):
        self._entity_id = entity_id
        self._text = text

    @property
    def entity_id(self):
        return self._entity_id

    @property
    def text(self):
        return self._text

    @property
    def dbpedia_id(self):
         return page_id_to_DBpedia_id(self._entity_id)
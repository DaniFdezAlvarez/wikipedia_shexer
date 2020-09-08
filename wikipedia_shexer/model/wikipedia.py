class Abstract (object):

    def __init__(self, page_id, sentences=None, text=None):
        self._page_id = page_id
        self._sentences = sentences if sentences is not None else []
        self._text = text

    def add_sentence(self, sentence):
        self._sentences.append(sentence)


class Sentence (object):
    def __init__(self, mentions=None, text=None):
        self._mentions = mentions if mentions is not None else []
        self._text = text

    def add_mention(self, mention):
        self._mentions.append(mention)


class Mention(object):
    def __init__(self, entity_id, text=None):
        self._entity_id = entity_id
        self._text = text

class TypingCache(object):

    def __init__(self, source_file, filter_out_of_dbpedia=True, discard_superclasses=True):

        self._filter_not_dbpedia = filter_out_of_dbpedia
        self._discard_superclasses = discard_superclasses

        self._type_dict = {}

        self._load_type_cache(source_file)

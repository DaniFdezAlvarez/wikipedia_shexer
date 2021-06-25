
class DBpediaDumpDigger(object):

    def __init__(self, source_files, root_entities=None):
        self._source_files = source_files

    def true_triples_of_model_abstract(self, m_abstract):
        pass  # TODO

    def true_triples_of_model_abstracts(self, model_abstracts_list):
        """
        In case you want to get the true triples of several model abstracts, please use
        this method instead of true_triples_of_model_abstract. Both iterate over a local file.
        But this one will iterate a single time for the whole abstracts, while the other one will
        iterate n times for n abstracts.

        :param model_abstracts_list:
        :return:
        """
        pass  # TODO


from wikipedia_shexer.core.wikipedia_shape_extractor import WikipediaShapeExtractor
from sklearn import svm

class LarewaExtractor(object):
    """
    Automatic shape extractor from Wikipedia abstracts based on a language-agnostic approach.

    """

    def __init__(self, ontology_file,
                 typing_file,
                 wikilinks_file=None,
                 wikipedia_dump_file=None,
                 all_classes_mode=True,
                 callback=svm.SVC,
                 include_typing_triples=True,
                 shape_threshold=0):
        """

        :param ontology_file: path to owl File with DBpedia basic ontology (DBO classes and properties)
        :param typing_file: path to ttl file with DBpedia typings
        :param wikilinks_file: path to ttl file with links between Wikipedia pages stored in DBpedia
        :param wikipedia_dump_file: path to Wikipedia XML dump file
        :param all_classes_mode: parameter for sheXer. It indicates if sheXer should extarct a shape for every
        class with at least an instance.
        :param callback: machine learning algorithm. Choose a sklearn class which can be used to create classifiers,
        such as sklearn.svm.SVC (default)
        :param include_typing_triples: the triples generated from wikipedia abstract will include typings
        parsed from the typings file, not just triples extracted from the actual abstracts
        :param shape_threshold: paremeter for sheXer. It indecates minimun trustworthy score,
        i.e., minimum rate of instance support, for a constraint to be accepted in a shape.
        """
        self._all_classes_mode=all_classes_mode
        self._callback=callback
        self._include_typing_triples=include_typing_triples
        self._shape_threshold = shape_threshold
        self._wikipedia_dump_file = wikipedia_dump_file
        self._extractor = WikipediaShapeExtractor(typing_file=typing_file,
                                                  wikilinks_file=wikilinks_file,
                                                  ontology_file=ontology_file,
                                                  all_classes_mode=True)

    def extract_shapes_from_rows(self, training_data_file,
                                 new_rows_file,
                                 triples_out_file,
                                 shapes_out_file):
        """

        Method to extract shapes from an already existing file of extracted features

        :param training_data_file: path to csv file with training data
        :param new_rows_file: path to csv file to serialize new features.
        :param triples_out_file: path to ttl file for storing the triples extracted
        :param shapes_out_file: path to ttl file for storing the shapes extracted
        :return:
        """
        self._extractor.extract_shapes_of_rows(rows_file=new_rows_file,
                                               triples_out_file=triples_out_file,
                                               shapes_out_file=shapes_out_file,
                                               training_data_file=training_data_file,
                                               callback=self._callback,
                                               include_typing_triples=self._include_typing_triples,
                                               shape_threshold=self._shape_threshold)

    def extract_shapes_from_titles_file(self, titles_file, rows_out_file,
                                        triples_out_file, shapes_out_file,
                                        training_data_file=None, inverse=True):
        """

        Method to extract shapes from a list of Wikipedia abstracts

        :param titles_file: path to file containing a Wikipedia title page per row.
        :param rows_out_file: path to csv file to serialize new features.
        :param triples_out_file: path to ttl file for storing the triples extracted
        :param shapes_out_file: path to ttl file for storing the shapes extracted
        :param training_data_file: (optional)  path to csv file with training data already existing
        :param inverse: boolean that indicates if the triple extractor should extract inverse triples
        too, i.d., triples where the target titles act as object
        :return:
        """
        self._extractor.extract_shapes_of_titles_file(titles_file=titles_file,
                                                      rows_out_file=rows_out_file,
                                                      triples_out_file=triples_out_file,
                                                      shapes_out_file=shapes_out_file,
                                                      training_data_file=training_data_file,
                                                      callback=self._callback,
                                                      inverse=inverse,
                                                      include_typing_triples=self._include_typing_triples,
                                                      shape_threshold=self._shape_threshold,
                                                      wikipedia_dump_file=self._wikipedia_dump_file)




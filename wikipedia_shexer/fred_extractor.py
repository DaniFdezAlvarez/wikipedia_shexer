from wikipedia_shexer.wesofred.wes_fredapi import _MIN_TIME_BETWEEN_REQ
from shexer.consts import SHEXC
from wikipedia_shexer.core.fred_shape_extractor import FredShapeExtractor

class FredExtractor(object):
    """
    Automatic shape extractor from Wikipedia abstracts based on FRED.

    """

    def __init__(self, api_key,
                 min_time_between=_MIN_TIME_BETWEEN_REQ,
                 n_retries_query=1,
                 all_classes_mode=True,
                 target_classes=None,
                 shape_threshold=0,
                 shapes_format=SHEXC,
                 wikipedia_dump_file=None):
        """

        :param api_key: (str) api Key for the FRED subsystem
        :param min_time_between: (int) seconds to wait between petitions to FRED
        :param n_retries_query: (int) number of times to retry a failed query
        :param all_classes_mode: (bool) parameter for sheXer. It indicates if sheXer should extarct a shape for every
        class with at least an instance.
        :param target_classes: optional, list of URIs (str). The extractor will only produce shapes for the classes
        in this list.
        :param shape_threshold: (float between 0 and 1) Paremeter for sheXer. It indecates minimun trustworthy score,
        i.e., minimum rate of instance support, for a constraint to be accepted in a shape.
        :param shapes_format: (str) Format to serialize the obtained shapes. One of the shape formats in shexer.consts
        :param wikipedia_dump_file: (str) path to Wikipedia XML dump file
        """
        self._extractor = FredShapeExtractor(api_key=api_key,
                                              petitions_already_performed=0,
                                              min_time_between=min_time_between,
                                              n_retries_query=n_retries_query,
                                              all_classes_mode=all_classes_mode,
                                              target_classes=target_classes
                                              )
        self._shape_threshold=shape_threshold
        self._shapes_format = shapes_format
        self._wikipedia_dump_file = wikipedia_dump_file

    def extract_shapes_of_titles_file(self,
                                      titles_file,
                                      triples_out_file,
                                      shapes_out_file,
                                      inverse=True):
        """

        Method to extract shapes from a list of Wikipedia abstracts

        :param titles_file: (str) path to file containing a Wikipedia title page per row.
        :param triples_out_file: (str) path to ttl file for storing the triples extracted
        :param shapes_out_file: (str) path to ttl file for storing the shapes extracted
        :param inverse: (bool) boolean that indicates if the triple extractor should extract inverse triples
        :return:
        """
        self._extractor.extract_shapes_of_titles_file(titles_file=titles_file,
                                                      triples_out_file=triples_out_file,
                                                      shapes_out_file=shapes_out_file,
                                                      inverse=inverse,
                                                      shapes_format=self._shapes_format,
                                                      shape_threshold=self._shape_threshold,
                                                      wikipedia_dump_file=self._wikipedia_dump_file)


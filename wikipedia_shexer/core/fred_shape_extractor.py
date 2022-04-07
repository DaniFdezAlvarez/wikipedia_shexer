from shexer.consts import SHEXC, NT
from shexer.shaper import Shaper
from wikipedia_shexer.wesofred.wes_fredapi import _MIN_TIME_BETWEEN_REQ
from wikipedia_shexer.core.fred_triple_extractor import FredTripleExtractor


class FredShapeExtractor(object):

    def __init__(self,
                 api_key,
                 petitions_already_performed=0,
                 min_time_between=_MIN_TIME_BETWEEN_REQ,
                 n_retries_query=1,
                 all_classes_mode=True,
                 target_classes=None):
        """
        :param all_classes_mode: boolean
        :param target_classes:  can be a list of URIs (str)
        """

        self._all_classes_mode = all_classes_mode
        self._target_classes = target_classes

        self._wikipedia_triple_extractor = None
        self._api_key = api_key

        self._petitions_already_performed = petitions_already_performed
        self._time_between = min_time_between
        self._retry = n_retries_query

        self._triple_extractor = None  # Will be initialized later


    def extract_shapes_of_titles_file(self,
                                      titles_file,
                                      triples_out_file,
                                      shapes_out_file,
                                      inverse=True,
                                      shapes_format=SHEXC,
                                      shape_threshold=0.1,
                                      wikipedia_dump_file=None):
        self._generate_triples_from_titles(titles_file=titles_file,
                                           triples_out_file=triples_out_file,
                                           wikipedia_dump_file=wikipedia_dump_file)
        self._generate_shapes(shapes_out_file=shapes_out_file,
                              format=shapes_format,
                              shape_threshold=shape_threshold,
                              triples_out_file=triples_out_file,
                              inverse=inverse)

    @property
    def petitions_performed(self):
        return self._triple_extractor.petitions_performed

    def _generate_shapes(self,
                         shapes_out_file,
                         format,
                         shape_threshold,
                         triples_out_file,
                         inverse=True):
        shaper = Shaper(all_classes_mode=self._all_classes_mode,
                        target_classes=self._target_classes,
                        graph_file_input=triples_out_file,
                        input_format=NT,
                        inverse_paths=inverse,
                        namespaces_dict=FredShapeExtractor.default_namespaces())
        shaper.shex_graph(output_file=shapes_out_file,
                          acceptance_threshold=shape_threshold,
                          output_format=format)

    def _generate_triples_from_titles(self,
                                      titles_file,
                                      triples_out_file,
                                      wikipedia_dump_file):

        self._triple_extractor = FredTripleExtractor(api_key=self._api_key,
                                                     petitions_already_performed=self._petitions_already_performed,
                                                     min_time_between=self._time_between,
                                                     n_retries_query=self._retry)
        try:
            self._triple_extractor.extract_triples_of_titles_file(titles_file=titles_file,
                                                                  triples_out_file=triples_out_file,
                                                                  wikipedia_dump_file=wikipedia_dump_file)
        except BaseException as e:
            print("The triple extractor could not complete all the petitions. Last message: {}"
                  "\n\nA shape for the data already gathered is going to be generated".format(e))

        self._petitions_already_performed = self._triple_extractor.petitions_performed

    @staticmethod
    def default_namespaces():
        return {
            "http://www.w3.org/XML/1998/namespace/": "xml",
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
            "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
            "http://www.w3.org/2001/XMLSchema#": "xsd",
            "http://xmlns.com/foaf/0.1/": "foaf",
            "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#" : "dul",
            "https://w3id.org/framester/schema/" : "framester",
            "http://www.ontologydesignpatterns.org/ont/fred/domain.owl#" : "fred",
            "http://schema.org/" : "schema",
            "http://www.ontologydesignpatterns.org/ont/framenet/abox/fe/" : "fe",
            "http://www.ontologydesignpatterns.org/ont/boxer/boxer.owl#" : "boxer",
            "http://dbpedia.org/resource/" : "dbr",
            "http://dbpedia.org/ontology/": "dbo",
            "http://www.ontologydesignpatterns.org/ont/boxer/boxing.owl#" : "boxing"
        }
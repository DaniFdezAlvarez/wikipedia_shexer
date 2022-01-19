from wikipedia_shexer.core.wikipedia_triple_extractor import WikipediaTripleExtractor
from shexer.consts import SHEXC, NT
from shexer.shaper import Shaper


class WikipediaShapeExtractor(object):

    def __init__(self, typing_file,
                 wikilinks_file,
                 ontology_file,
                 all_classes_mode=True,
                 target_classes=None):
        """

        :param typing_file: str path
        :param wikilinks_file: str path
        :param ontology_file: str path
        :param all_classes_mode: boolean
        :param target_classes:  can be a list of URIs (str)
        """
        self._typing_file = typing_file
        self._wikilinks_file = wikilinks_file
        self._ontology_file = ontology_file

        self._all_classes_mode = all_classes_mode
        self._target_classes = target_classes

    def extract_shapes_of_rows(self,
                               rows_file,
                               triples_out_file,
                               shapes_out_file,
                               training_data_file,
                               callback,
                               include_typing_triples=True,
                               shapes_format=SHEXC,
                               shape_threshold=0.1
                               ):
        self._generate_triples_from_rows(rows_file=rows_file,
                                         triples_out_file=triples_out_file,
                                         training_data_file=training_data_file,
                                         callback=callback,
                                         include_typing_triples=include_typing_triples)
        self._generate_shapes(shapes_out_file=shapes_out_file,
                              format=shapes_format,
                              shape_threshold=shape_threshold,
                              triples_out_file=triples_out_file)
        

    def extract_shapes_of_titles_file(self,
                                      titles_file,
                                      rows_out_file,
                                      triples_out_file,
                                      shapes_out_file,
                                      training_data_file,
                                      callback,
                                      inverse=True,
                                      include_typing_triples=True,
                                      shapes_format=SHEXC,
                                      shape_threshold=0.1,
                                      wikipedia_dump_file=None):

        self._generate_triples_from_titles(titles_file=titles_file,
                                           rows_out_file=rows_out_file,
                                           triples_out_file=triples_out_file,
                                           training_data_file=training_data_file,
                                           callback=callback,
                                           inverse=inverse,
                                           include_typing_triples=include_typing_triples,
                                           wikipedia_dump_file=wikipedia_dump_file)
        self._generate_shapes(shapes_out_file=shapes_out_file,
                              format=shapes_format,
                              shape_threshold=shape_threshold,
                              triples_out_file=triples_out_file,
                              inverse=inverse)

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
                        inverse_paths=inverse)
        shaper.shex_graph(output_file=shapes_out_file,
                          acceptance_threshold=shape_threshold,
                          output_format=format)


    def _generate_triples_from_titles(self, 
                                      titles_file,
                                      rows_out_file,
                                      triples_out_file,
                                      training_data_file,
                                      callback,
                                      inverse,
                                      include_typing_triples,
                                      wikipedia_dump_file):
        WikipediaTripleExtractor(
            typing_file=self._typing_file,
            ontology_file=self._ontology_file,
            wikilinks_file=self._wikilinks_file
        ).extract_triples_of_titles_file(
            titles_file=titles_file,
            rows_out_file=rows_out_file,
            triples_out_file=triples_out_file,
            training_data_file=training_data_file,
            callback=callback,
            inverse=inverse,
            include_typing_triples=include_typing_triples,
            wikipedia_dump_file=wikipedia_dump_file
        )
        
    def _generate_triples_from_rows(self, 
                                      rows_file,
                                      triples_out_file,
                                      training_data_file,
                                      callback,
                                      include_typing_triples):
        WikipediaTripleExtractor(
            typing_file=self._typing_file,
            ontology_file=self._ontology_file,
            wikilinks_file=self._wikilinks_file
        ).extract_triples_of_rows(
            rows_file=rows_file,
            triples_out_file=triples_out_file,
            training_data_file=training_data_file,
            callback=callback,
            include_typing_triples=include_typing_triples
        )

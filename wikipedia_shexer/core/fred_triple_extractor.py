from wikipedia_shexer.wesofred.wes_fredapi import WesFredApi, _MIN_TIME_BETWEEN_REQ
from wikipedia_shexer.core.wikipedia_dump_extractor import WikipediaDumpExtractor
from wikipedia_shexer.io.csv import CSVYielderQuotesFilter
from wikipedia_shexer.io.line_reader.file_line_reader import FileLineReader
from rdflib import Graph, URIRef, OWL, RDF
import time

_S = 0
_P = 1
_O = 2
_AVOID_TARGET_PROPERTIES = [
    OWL.sameAs,
    URIRef("http://www.ontologydesignpatterns.org/ont/boxer/boxer.owl#possibleType"),
    URIRef("http://www.ontologydesignpatterns.org/ont/fred/quantifiers.owl#hasDeterminer")
]

def print_triples(triples, msg):
    print("-------------")
    print(msg)
    print("-------------")
    for a_triple in triples:
        print("[ {} {} {} ]".format(a_triple[_S], a_triple[_P], a_triple[_O]))

class FredTripleExtractor(object):

    def __init__(self, api_key, petitions_already_performed=0,min_time_between=_MIN_TIME_BETWEEN_REQ,
                 n_retries_query=1):
        self._api = WesFredApi(api_key=api_key,
                               petitions_already_performed=petitions_already_performed,
                               min_time_between=min_time_between)
        self._retry = n_retries_query

    def extract_triples_of_titles_file(self,
                                       titles_file,
                                       triples_out_file,
                                       wikipedia_dump_file):
        dump_extractor = WikipediaDumpExtractor(wikipedia_dump_file=wikipedia_dump_file,
                                                dbpedia_source_files=None)  # Nothing to do with true triples here
        page_list = self._target_instances_from_file(titles_file=titles_file)
        init = time.time()
        print("Starting model extraction, {} targets...".format(len(page_list)))
        models = dump_extractor.extract_titles_model(list_of_titles=page_list,
                                                     fill_true_triples=False)
        print("Models extracted. Time used: {} minutes".format((time.time()-init) / 60))
        self._process_models(models, triples_out_file)

    @property
    def petitions_performed(self):
        return self._api.petitions_performed

    def _process_models(self, models, triples_out_file):
        self._reset_triples_out_file(triples_out_file)
        for a_model in models:
            self._compute_model(a_model, triples_out_file)

    def _reset_triples_out_file(self, triples_out_file):
        with open(triples_out_file, "w") as out_stream:
            out_stream.write("")

    def _compute_model(self, model, triples_out_file):
        pairs = self._split_model_in_sentence_pairs(model)
        for a_pair in pairs:
            try:
                rdflib_graph = self._get_graph_from_pair(a_pair)
                target_triples = self._get_target_triples_from_graph(rdflib_graph, target_dbpedia_id=model.dbpedia_id)
                self._serialize_triples(target_triples=target_triples,
                                        target_file=triples_out_file)
            except BaseException as e:
                print("Last model computed: {}\nLast sentnces attempted:{}".format(model.page_id,
                                                                                   " ".join(a_pair)))
                raise e

    def _get_target_triples_from_graph(self, rdflib_graph, target_dbpedia_id):
        # TODO 1: locate X owl:sameAs target_dbpedia_id
        # TODO 2: locate every triple (X, p, Yi) y (Yi, p, X)  Maybe filter some of them (ow:sameAs, possibleType)
        # TODO 3: change X by dbpedia_id in all those triples and store them
        # TODO 4: add typing triples for every Yi. For a given Yi, if there are several types and one is a DBpedia type,
        # TODO 4BIS: ... maybe just use the DBpedia one. Or no... I dunno
        dbpedia_uriref = URIRef(target_dbpedia_id)
        target = self._find_dbpedia_equivalent_target_node(graph=rdflib_graph,
                                                           dbpedia_uriref=dbpedia_uriref)
        print("target node! {}".format(target))
        if target is None:
            return []
        # The typed of the target node are included in the following line
        target_triples = self._find_triples_of_target_node(target_node=target,
                                                           graph=rdflib_graph)
        print_triples(target_triples, "Triples involving target node")

        target_triples = self._replace_target_by_dbpedia_id(target_node=target,
                                                            triples= target_triples,
                                                            dbpedia_uriref=dbpedia_uriref)
        print_triples(target_triples, "Triples after changing by dbpedia id")

        # The typs of both satellitals and the original dbbedia is uncluded in the following line
        typings = self._add_satellital_node_types(target_triples=target_triples,
                                                          graph=rdflib_graph)
        print_triples(typings, "Satellital types")
        target_triples += typings
        return target_triples

    def _add_satellital_node_types(self, target_triples, graph):
        targets = set()
        result = []
        for a_triple in target_triples:
            if type(a_triple[_S]) == URIRef:
                targets.add(a_triple[_S])
            if type(a_triple[_O]) == URIRef:
                targets.add(a_triple[_O])
        for a_target in targets:
            for a_triple in graph.triples( (a_target, RDF.type, None) ):
                result.append(a_triple)
        return result

    def _replace_target_by_dbpedia_id(self, target_node, triples, dbpedia_uriref):
        return ([self._replace_target_obj_and_subj_if_needed(triple=triple,
                                                             target=target_node,
                                                             dbpedia_uriref=dbpedia_uriref) for triple in triples])

    def _replace_target_obj_and_subj_if_needed(self, triple, target, dbpedia_uriref):
        return (
            triple[_S] if triple[_S] != target else dbpedia_uriref,
            triple[_P],
            triple[_O] if triple[_O] != target else dbpedia_uriref,
        )

    def _is_relevant_target_triple(self, a_triple):
        return a_triple[_P] not in _AVOID_TARGET_PROPERTIES

    def _find_triples_of_target_node(self, target_node, graph):
        result = [triple for triple in graph.triples((target_node, None, None)) if self._is_relevant_target_triple(triple)]
        result += [triple for triple in graph.triples((None, None, target_node)) if self._is_relevant_target_triple(triple)]
        return result

    def _find_dbpedia_equivalent_target_node(self, graph, dbpedia_uriref):
        triples = [ triple for triple in graph.triples((None, OWL.sameAs, dbpedia_uriref))]
        if len(triples) == 0:
            return None
        if len(triples) == 1:
            return triples[0][_S]  # Subject of the first (and only) tuple in triples
        else:
            raise ValueError("The graph received contaisn more than one equivalent class to {}.".format(dbpedia_uriref))

    def _serialize_triples(self, target_triples, target_file):
        if len(target_triples) == 0:
            return
        with open(target_file, "a") as out_str_append:
            out_str_append.write("\n")
            out_str_append.write("\n".join(self._3tuple_to_ntriples_format(a_triple) for a_triple in target_triples))

    def _3tuple_to_ntriples_format(self, a_rdflib_3tuple):
        if type(a_rdflib_3tuple[2]) == URIRef:
            return "<{}> <{}> <{}> .".format(a_rdflib_3tuple[0],
                                             a_rdflib_3tuple[1],
                                             a_rdflib_3tuple[2])
        return "<{}> <{}> {} .".format(a_rdflib_3tuple[0],
                                       a_rdflib_3tuple[1],
                                       a_rdflib_3tuple[2].n3())




    def _get_graph_from_pair(self, sentence_2tuple):
        try:
            return self._api.get_rdflib_graph("".join(sentence_2tuple))
        except BaseException as e:
            return self._get_graph_from_splitted_pair(sentence_2tuple=sentence_2tuple,
                                                      retry=self._retry)

    def _get_graph_from_splitted_pair(self, sentence_2tuple, retry):
        result = Graph()
        for a_sentence in sentence_2tuple:
            result.parse(self._get_sentence_raw_graph(a_sentence, retry), format="xml")
        return result

    def _get_sentence_raw_graph(self, sentence, retry: int):
        """
        :param sentence:
        :param retry: nº of times to retry a query
        :return:
        """
        while True:
            try:
                return self._api.get_str_graph(text=sentence)
            except BaseException as e:
                retry -= 1
                if retry < 0:
                    raise e

    def _split_model_in_sentence_pairs(self, a_model):
        result = []
        hub = []
        for a_sentence in a_model.sentences():
            hub.append(self._trailing_dot(a_sentence.text))
            if len(hub) == 2:
                result.append( (hub[0], hub[1]))
                hub = []
        if len(hub) == 1:
            result.append((hub[0], ""))
        return result

    def _trailing_dot(self, text_sentence):
        if text_sentence.endswith("."):
            return text_sentence
        return text_sentence + "."

    def _target_instances_from_file(self, titles_file):
        uris_yielder = CSVYielderQuotesFilter(
            FileLineReader(
                source_file=titles_file
            )
        )
        return uris_yielder.list_lines()
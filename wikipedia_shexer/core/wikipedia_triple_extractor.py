from wikipedia_shexer.model.ontology import Ontology
from wikipedia_shexer.utils.cache import TypingCache, BackLinkCache
from wikipedia_shexer.features.feature_extractor import FeatureExtractor
from wikipedia_shexer.io.csv import CSVYielderQuotesFilter
from wikipedia_shexer.io.line_reader.file_line_reader import FileLineReader
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

COL_NAMES = ["prop", "instance", "mention", "positive", "direct", "cand_abs",
             "cand_sen", "rel_cand_abs", "rel_cand_sen", "ent_sen", "rel_ent_a",
             "rel_ent_sen", "rel_sen_abs", "back_link"]

FEATURE_COLS = ["direct", "cand_abs", "cand_sen", "rel_cand_abs", "rel_cand_sen",
                "ent_sen", "rel_ent_a", "rel_ent_sen", "rel_sen_abs", "back_link"]
MIN_SAMPLE = 20

class WikipediaTripleExtractor(object):

    def __init__(self, typing_file,
                 wikilinks_file,
                 ontology_file):
        self._typing_file = typing_file
        self._wikilinks_file = wikilinks_file
        self._ontology_file = ontology_file

        # self._ontology = None
        # self._back_link_cache = None
        # self._typing_cache = None
        self._f_extractor = None
        self._clf_battery = {}  # Will be a dict {'str_prop' --> classifier (trained)}
        self._target_data = None # Will contain a dataframe with the extracted rows

    def extract_triples_of_titles_file(self,
                                       titles_file,
                                       rows_out_file,
                                       triples_out_file,
                                       training_data_file,
                                       callback,
                                       inverse=True):
        self._load_internal_strcutures()
        self._f_extractor.rows_to_file_from_page_list(page_list=self._target_instances(titles_file),
                                                      inverse=inverse,
                                                      file_path=rows_out_file)
        self._load_classifiers(training_data_file=training_data_file,
                               callback=callback)
        self._write_predicted_triples(triples_out_file=triples_out_file,
                                      rows_out_file=rows_out_file)  # TODO


    def _write_predicted_triples(self, triples_out_file, rows_out_file):
        with open(triples_out_file, "w") as out_str:
            for prop_key in self._clf_battery:
                self._write_triples_for_a_prop_model(
                    out_stream=out_str,
                    prop_key=prop_key,
                    rows_out_file=rows_out_file)

    def _write_triples_for_a_prop_model(self, prop_key, out_stream, rows_out_file):
        target_data = self._load_prop_target_data(prop_key=prop_key,
                                                  rows_out_file=rows_out_file)
        X = target_data[FEATURE_COLS]
        # y = target_data.positive.astype('int')
        clf = self._clf_battery[prop_key]
        y_pred = clf.predict(X)
        self._write_actual_triples(X_data=X,
                                   y_results=y_pred,
                                   prop_key=prop_key,
                                   out_stream=out_stream)

    def _write_actual_triples(self, X_data, y_results, prop_key, out_stream):
        """
        FIND POSITIVE ROWS IN Y_RESUTLS AND GENERATE THE CORRESPONDING
        TRIPLE USING DATA OF X_DATA AND PROP_KEY
        ÇOYT_STREAM IS AN ALREADY OPEN STREAM TO WRITE LINES

        :param X_data:
        :param y_results:
        :param prop_key:
        :param out_stream:
        :return:
        """
        pass  # TODO

    def _load_prop_target_data(self, prop_key, rows_out_file):
        if self._target_data is None:
            self._read_target_data(rows_out_file)
        return self._target_data[self._target_data['prop'] == prop_key]

    def _read_target_data(self, rows_out_file):
        self._target_data = pd.read_csv(rows_out_file, header=None, names=COL_NAMES, sep=";")



    def _load_internal_strcutures(self):
        ontology = Ontology(source_file=self._ontology_file)
        typing_cache = TypingCache(source_file=self._typing_file,
                                   ontology=ontology,
                                   filter_out_of_dbpedia=True,
                                   discard_superclasses=True)
        back_link_cache = BackLinkCache(source_file=self._wikilinks_file)
        self._f_extractor = FeatureExtractor(ontology=ontology,
                                             type_cache=typing_cache,
                                             backlink_cache=back_link_cache)

    def _target_instances(self, titles_file):
        uris_yielder = CSVYielderQuotesFilter(
            FileLineReader(
                source_file=titles_file
            )
        )
        return uris_yielder.list_lines()

    def _load_classifiers(self, training_data_file, callback):
        features = pd.read_csv(training_data_file, header=None, names=COL_NAMES, sep=";")
        for a_prop in set(features['prop']):
            prop_features = features[features['prop'] == a_prop]
            if len(features > MIN_SAMPLE):
                pass
            X = prop_features[FEATURE_COLS]
            y = prop_features.positive.astype('int')
            if len(np.unique(y)) <= 1:
                return 1.0
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)
            a_clasiff = callback().fit(X_train, y_train)
            self._clf_battery[a_prop] = a_clasiff
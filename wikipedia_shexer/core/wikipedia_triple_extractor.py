from wikipedia_shexer.model.ontology import Ontology
from wikipedia_shexer.utils.cache import TypingCache, BackLinkCache
from wikipedia_shexer.features.feature_extractor import FeatureExtractor
from wikipedia_shexer.io.csv import CSVYielderQuotesFilter
from wikipedia_shexer.io.line_reader.file_line_reader import FileLineReader
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import page_id_to_DBpedia_id
from wikipedia_shexer.const import NAME_COLS, FEATURE_COLS, COL_DIRECT, COL_INSTANCE, \
    COL_MENTION, COL_PROP, COL_POSITIVE, COL_BACK_LINK

_TRIPLE_PATTERN = "<{}> <{}> <{}> .\n"

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
        self._target_data = None  # Will contain a dataframe with the extracted rows

    def extract_triples_of_titles_file(self,
                                       titles_file,
                                       rows_out_file,
                                       triples_out_file,
                                       training_data_file,
                                       callback,
                                       inverse=True):
        self._load_internal_structures()
        self._f_extractor.rows_to_file_from_page_list(page_list=self._target_instances(titles_file),
                                                      inverse=inverse,
                                                      file_path=rows_out_file)
        self._load_classifiers(training_data_file=training_data_file,
                               callback=callback)
        self._write_predicted_triples(triples_out_file=triples_out_file,
                                      rows_source_file=rows_out_file)

    def extract_triples_of_rows(self,
                                rows_file,
                                triples_out_file,
                                training_data_file,
                                callback):
        self._load_classifiers(training_data_file=training_data_file,
                               callback=callback)
        self._write_predicted_triples(triples_out_file=triples_out_file,
                                      rows_source_file=rows_file)

    def _write_predicted_triples(self, triples_out_file, rows_source_file):
        with open(triples_out_file, "w", encoding="utf-8") as out_str:
            for prop_key in self._clf_battery:
                self._write_triples_for_a_prop_model(
                    out_stream=out_str,
                    prop_key=prop_key,
                    rows_out_file=rows_source_file)

    def _write_triples_for_a_prop_model(self, prop_key, out_stream, rows_out_file):
        target_data = self._load_prop_target_data(prop_key=prop_key,
                                                  rows_out_file=rows_out_file)
        X = target_data[FEATURE_COLS]
        # y = target_data.positive.astype('int')
        clf = self._clf_battery[prop_key]
        y_pred = clf.predict(X)
        self._write_actual_triples(target_data=target_data,
                                   y_results=y_pred,
                                   out_stream=out_stream)

    def _write_actual_triples(self, target_data, y_results, out_stream):
        index = 0
        for row in target_data.iterrows():
            if y_results[index] == 1:
                self._write_triple(out_stream=out_stream,
                                   triple=self._build_triple_from_row(row[1]))
            index += 1

    def _write_triple(self, out_stream, triple):
        out_stream.write(_TRIPLE_PATTERN.format(triple[0],
                                                triple[1],
                                                triple[2]))

    def _build_triple_from_row(self, row):
        if row[COL_DIRECT] == 1:
            return (
                page_id_to_DBpedia_id(row[COL_INSTANCE]),
                row[COL_PROP],
                page_id_to_DBpedia_id(row[COL_MENTION])
            )
        else:
            return (
                page_id_to_DBpedia_id(row[COL_MENTION]),
                row[COL_PROP],
                page_id_to_DBpedia_id(row[COL_INSTANCE])
            )

    def _load_prop_target_data(self, prop_key, rows_out_file):
        if self._target_data is None:
            self._read_target_data(rows_out_file)
        return self._target_data[self._target_data[COL_PROP] == prop_key]

    def _read_target_data(self, target_file):
        self._target_data = self._read_pandas_csv(target_file=target_file)

    def _load_internal_structures(self):
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
        features = self._read_pandas_csv(target_file=training_data_file)
        for a_prop in set(features[COL_PROP]):
            prop_features = features[features[COL_PROP] == a_prop]
            if len(prop_features) > MIN_SAMPLE:
                X = prop_features[FEATURE_COLS]
                y = prop_features.positive.astype('int')
                values = np.unique(y)
                if len(values) == 1:
                    self._clf_battery[a_prop] = self._dumb_classifier(value=values[0])
                else:
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)
                    a_clasiff = callback().fit(X_train, y_train)
                    self._clf_battery[a_prop] = a_clasiff

    def _dumb_classifier(self, value):
        return DumbClassifier(value=value)

    def _read_pandas_csv(self, target_file):
        features = pd.read_csv(target_file, header=None, names=NAME_COLS, sep=";")
        self._map_bool_to_integer(dataframe=features, target_cols=[COL_POSITIVE, COL_BACK_LINK, COL_DIRECT])
        return features

    @staticmethod
    def _map_bool_to_integer(dataframe, target_cols):
        for i in range(len(dataframe)):
            for col_name in target_cols:
                dataframe.at[i, col_name] = 1 if dataframe.at[i, col_name] == 'True' else 0


class DumbClassifier(object):

    def __init__(self, value):
        self._value = value

    def predict(self, dataframe):
        return np.array([self._value for _ in range(len(dataframe))])
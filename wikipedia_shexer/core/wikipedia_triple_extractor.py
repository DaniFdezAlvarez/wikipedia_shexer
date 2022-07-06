from wikipedia_shexer.model.ontology import Ontology
from wikipedia_shexer.utils.cache import TypingCache, BackLinkCache
from wikipedia_shexer.features.feature_extractor import FeatureExtractor
from wikipedia_shexer.io.csv import CSVYielderQuotesFilter
from wikipedia_shexer.io.line_reader.file_line_reader import FileLineReader
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import metrics
from wikipedia_shexer.utils.wikipedia_dbpedia_conversion import page_id_to_DBpedia_id
from wikipedia_shexer.const import NAME_COLS, FEATURE_COLS, COL_DIRECT, COL_INSTANCE, \
    COL_MENTION, COL_PROP, COL_POSITIVE, COL_BACK_LINK

_TRIPLE_PATTERN = "<{}> <{}> <{}> .\n"
_S = 0
_P = 1
_O = 2
_RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

MIN_SAMPLE = 14
MIN_ACCURACY_MODEL = 0.75


class WikipediaTripleExtractor(object):

    def __init__(self, typing_file,
                 wikilinks_file,
                 ontology_file):
        self._typing_file = typing_file
        self._wikilinks_file = wikilinks_file
        self._ontology_file = ontology_file

        # Will be initialized in lazy mode when needed (if needed)
        self._ontology = None
        self._back_link_cache = None
        self._typing_cache = None
        self._f_extractor = None

        self._clf_battery = {}  # Will be a dict {'str_prop' --> {1 : classifier, 0 : classifier}}
                                # 1 and 0 are keys for direct or inverse direction triples.
                                # the added classifiers should be already trained
        self._target_data = None  # Will contain a dataframe with the extracted rows

        self._types_added = None  # Set that will be filled during the execution

        self._not_enough_training_data = 0
        self._dumb_classifiers = 0
        self._accepted_models_not_dumb = 0
        self._discarded_models = 0
        self._enough_training_data = 0
        self._at_least_a_positive_example = 0
        self._accepted_sizes = []
        self._accepted_scores = []
        self._candidate_properties = 0
        self._candidate_p_s_pairs = 0
        self._properties_with_a_model = set()

    def extract_triples_of_titles_file(self,
                                       titles_file,
                                       rows_out_file,
                                       triples_out_file,
                                       training_data_file,
                                       callback,
                                       inverse=True,
                                       include_typing_triples=True,
                                       wikipedia_dump_file=None):
        self._load_internal_structures()
        self._f_extractor.rows_to_file_from_page_list(page_list=self._target_instances_from_file(titles_file),
                                                      inverse=inverse,
                                                      file_path=rows_out_file,
                                                      training=False,
                                                      wikipedia_dump_file=wikipedia_dump_file)
        self._load_classifiers(training_data_file=training_data_file,
                               callback=callback)
        self._write_predicted_triples(triples_out_file=triples_out_file,
                                      rows_source_file=rows_out_file,
                                      include_typing_triples=include_typing_triples)

    def extract_triples_of_rows(self,
                                rows_file,
                                triples_out_file,
                                training_data_file,
                                callback,
                                include_typing_triples=True):
        self._load_internal_structures(need_typing=include_typing_triples,
                                       need_backlink=False,
                                       need_extractor=False)
        print("loading classifiers...")
        self._load_classifiers(training_data_file=training_data_file,
                               callback=callback)
        self._print_model_stats()
        print("writing predictions...")
        # self._write_predicted_triples(triples_out_file=triples_out_file,
        #                               rows_source_file=rows_file,
        #                               include_typing_triples=include_typing_triples)

    def _write_predicted_triples(self, triples_out_file, rows_source_file, include_typing_triples):
        with open(triples_out_file, "w", encoding="utf-8") as out_str:
            for prop_key in self._clf_battery:
                for a_sense in self._clf_battery[prop_key]:
                    self._write_triples_for_a_prop_sense_model(
                        out_stream=out_str,
                        prop_key=prop_key,
                        sense_key=a_sense,
                        rows_out_file=rows_source_file,
                        include_typing_triples=include_typing_triples)

    def _write_triples_for_a_prop_sense_model(self, prop_key, sense_key,
                                              out_stream, rows_out_file, include_typing_triples):
        target_data = self._load_prop_sense_target_data(prop_key=prop_key,
                                                        sense_key=sense_key,
                                                        rows_out_file=rows_out_file)
        X = target_data[FEATURE_COLS]
        if len(X) > 0:
            clf = self._clf_battery[prop_key][sense_key]
            y_pred = clf.predict(X)
            self._write_actual_triples(target_data=target_data,
                                       y_results=y_pred,
                                       out_stream=out_stream,
                                       include_typing_triples=include_typing_triples)

    def _write_actual_triples(self, target_data, y_results, out_stream, include_typing_triples):
        index = 0
        for row in target_data.iterrows():
            if y_results[index] == 1:
                a_triple = self._build_triple_from_row(row[1])
                self._write_triple(out_stream=out_stream,
                                   triple=a_triple)
                if include_typing_triples:
                    self._write_types_needed(a_triple=a_triple,
                                             out_stream=out_stream)
            index += 1

    def _write_types_needed(self, a_triple, out_stream):
        if a_triple[_S] not in self._types_added:
            self._write_type(a_node=a_triple[_S],
                             out_stream=out_stream)
        if a_triple[_O] not in self._types_added:
            self._write_type(a_node=a_triple[_O],
                             out_stream=out_stream)

    def _write_type(self, a_node, out_stream):
        self._types_added.add(a_node)
        for a_type in self._typing_cache.get_types_of_node(a_node):
            self._write_triple(out_stream=out_stream,
                               triple=(a_node, _RDF_TYPE, a_type))

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

    def _load_prop_sense_target_data(self, prop_key, sense_key, rows_out_file):
        self._read_target_data(rows_out_file)
        return self._target_data[(self._target_data[COL_PROP] == prop_key) & (self._target_data[COL_DIRECT] == sense_key)]

    def _read_target_data(self, target_file):
        self._target_data = self._read_pandas_csv(target_file=target_file)

    def _load_internal_structures(self, need_typing=True, need_backlink=True,
                                  need_extractor=True):
        self._types_added = set()
        if self._ontology is None:
            self._ontology = Ontology(source_file=self._ontology_file)
        if need_typing and self._typing_cache is None:
            self._typing_cache = TypingCache(source_file=self._typing_file,
                                             ontology=self._ontology,
                                             filter_out_of_dbpedia=True,
                                             discard_superclasses=True)
        if need_backlink and self._back_link_cache is None:
            self._back_link_cache = BackLinkCache(source_file=self._wikilinks_file)
        if need_extractor and self._f_extractor is None:
            self._f_extractor = FeatureExtractor(ontology=self._ontology,
                                                 type_cache=self._typing_cache,
                                                 backlink_cache=self._back_link_cache)

    def _target_instances_from_file(self, titles_file):
        uris_yielder = CSVYielderQuotesFilter(
            FileLineReader(
                source_file=titles_file
            )
        )
        return uris_yielder.list_lines()

    def _load_classifiers(self, training_data_file, callback):
        features = self._read_pandas_csv(target_file=training_data_file)
        props = set(features[COL_PROP])
        self._candidate_properties = len(props)
        self._candidate_p_s_pairs = len(props) * 2
        for a_prop in props:
            # print("Property {}:".format(a_prop))
            self._manage_property_classifiers(prop=a_prop,
                                              all_features=features,
                                              callback=callback)

    def _manage_property_classifiers(self, prop, all_features, callback):
        for is_direct in range(2):  # [0, 1]
            # print("Going for {}!".format("direct" if is_direct==1 else "inverse") )
            self._manage_property_sense_classifier(prop=prop,
                                                   all_features=all_features,
                                                   callback=callback,
                                                   direct_sense=is_direct
                                                   )
    def _manage_property_sense_classifier(self, prop, all_features, callback, direct_sense):
        # prop_features = features[features[COL_PROP] == a_prop]
        prop_sense_features = self._select_prop_sense_features(all_features=all_features,
                                                               prop=prop,
                                                               direct_sense=direct_sense)
        if len(prop_sense_features) >= 1:
            self._at_least_a_positive_example += 1
        if not self._trainig_has_min_sample_size(prop_sense_features):
            self._not_enough_training_data += 1
            # print("Discarded, not min samples. {} found, {} required".format(len(prop_sense_features), MIN_SAMPLE))
            return
        self._enough_training_data += 1

        X, y = self._get_feature_and_result_frames(prop_sense_features)
        if self._are_results_unique(y):
            # print("ACCEPTED! dumb classifier")
            self._properties_with_a_model.add(prop)
            self._accepted_scores.append(1)
            self._accepted_sizes.append(len(prop_sense_features))
            self._dumb_classifiers += 1
            self._manage_dumb_classifier(y, prop, direct_sense)
        else:
            self._manage_trained_classifier(X=X,
                                            y=y,
                                            prop=prop,
                                            direct_sense=direct_sense,
                                            callback=callback)

    def _manage_trained_classifier(self, X, y, prop, direct_sense, callback):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)
        if self._are_results_unique(y_train):
            self._properties_with_a_model.add(prop)
            self._dumb_classifiers += 1
            self._accepted_scores.append(1)
            self._accepted_sizes.append(len(X) + len(y))
            self._manage_dumb_classifier(y=y,
                                         prop=prop,
                                         direct_sense=direct_sense)
            return
        a_clasiff = callback().fit(X_train, y_train)
        y_pred = a_clasiff.predict(X_test)
        score = metrics.accuracy_score(y_test, y_pred)
        if score > MIN_ACCURACY_MODEL:
            self._accepted_models_not_dumb += 1
            self._properties_with_a_model.add(prop)
            # self._clf_battery[a_prop] = a_clasiff
            self._accepted_scores.append(score)
            self._accepted_sizes.append(len(X) + len(y))
            self._add_classifier_to_battery(classifier=a_clasiff,
                                            prop=prop,
                                            sense=direct_sense)
            # print("ACEPTED!!!!!!!!!!!!!!!!!!!!!!!!! ideal situation. precission of {}.".format(score))
        else:
            self._discarded_models += 1
            # print("Discarded! Due to unsafeness. precission of {}".format(score))


    def _manage_dumb_classifier(self, y, prop, direct_sense):
        self._add_classifier_to_battery(classifier=self._dumb_classifier(value=np.unique(y)[0]),
                                        prop=prop,
                                        sense=direct_sense)

    def _add_classifier_to_battery(self, classifier, prop, sense):
        if prop not in self._clf_battery:
            self._clf_battery[prop] = {}
        self._clf_battery[prop][sense] = classifier

    def _are_results_unique(self, y):
        return len(np.unique(y)) == 1

    def _get_feature_and_result_frames(self, dataframe):
        X = dataframe[FEATURE_COLS]
        y = dataframe.positive.astype('int')
        return X, y


    def _trainig_has_min_sample_size(self, dataframe):
        return len(dataframe) >= MIN_SAMPLE

    def _select_prop_sense_features(self, all_features, prop, direct_sense):
        return all_features[(all_features[COL_PROP] == prop) &  (all_features[COL_DIRECT] == direct_sense)]

    def _dumb_classifier(self, value):
        return DumbClassifier(value=value)

    def _read_pandas_csv(self, target_file):
        features = pd.read_csv(target_file, header=None, names=NAME_COLS, sep=";")
        self._map_bool_to_integer(dataframe=features, target_cols=[COL_POSITIVE, COL_BACK_LINK, COL_DIRECT])
        # self._map_bool_to_integer(dataframe=features, target_cols=[COL_POSITIVE])
        return features

    def _sorted_property_senses(self):
        result = []
        for a_prop_key, a_prop_dict in self._clf_battery.items():
            for a_sense_key in a_prop_dict:
                result.append(a_prop_key.replace("http://dbpedia.org/ontology/", "") + "_" + str(a_sense_key))
        result.sort()
        return "\n".join(result)

    def _print_model_stats(self):
        print("P-S with a positive example: {}".format(self._at_least_a_positive_example))
        print("P-S with at least 13 examples: {}".format(self._enough_training_data))
        total_accepted = self._dumb_classifiers + self._accepted_models_not_dumb
        print("Models accepted: {}".format(total_accepted))
        print("Properties with at least a model: {}".format(len(self._properties_with_a_model)))
        average_precission = sum(self._accepted_scores) / len(self._accepted_scores)
        print("Average precission among accepted models: {}".format(average_precission))
        average_size = sum(self._accepted_sizes)*1.0 / len(self._accepted_sizes)
        print("Average sample size accepted models: {}".format(average_size))
        diff_acum_score = 0.0
        for a_score in self._accepted_scores:
            diff_acum_score += abs(a_score - average_precission)
        print("STD dev scores: {}".format(diff_acum_score / len(self._accepted_scores)))
        diff_acum_size = 0.0
        for a_size in self._accepted_sizes:
            diff_acum_size += abs(a_size - average_size)
        print("STD dev scores: {}".format(diff_acum_size / len(self._accepted_sizes)))
        print("Sorted  P-S: \n{}".format(self._sorted_property_senses()))


    @staticmethod
    def _map_bool_to_integer(dataframe, target_cols):
        for col_name in target_cols:
            tmp = dataframe[col_name].astype(int)
            dataframe[col_name] = tmp
        # for i in range(len(dataframe)):
        #     for col_name in target_cols:
        #         tmp = dataframe[col_name].astype(int)
        #         dataframe[col_name] = tmp
        #        # dataframe.at[i, col_name] = 1 if dataframe.at[i, col_name] == 'True' else 0


class DumbClassifier(object):

    def __init__(self, value):
        self._value = value

    def predict(self, dataframe):
        return np.array([self._value for _ in range(len(dataframe))])

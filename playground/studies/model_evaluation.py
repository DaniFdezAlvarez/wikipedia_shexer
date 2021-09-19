import pandas as pd
import numpy as np
from sklearn import metrics
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split


def decission_tree():
    return DecisionTreeClassifier()

def svc():
    return svm.SVC()

def random_forest():
    return RandomForestClassifier()

def naive_bayes():
    return GaussianNB()

def logistic_reg():
    return LogisticRegression(max_iter=350)

def k_nearest():
    return KNeighborsClassifier()

def neural_netwrok():
    return MLPClassifier(max_iter=350)


def evaluate_prop(prop_name, features, callback):
    if len(features) < 20:
        # print("Not enough data to train a model")
        return None
    # print(prop_name, len(features))
    feature_cols = ["direct", "cand_abs", "cand_sen", "rel_cand_abs", "rel_cand_sen", "ent_sen", "rel_ent_a",
             "rel_ent_sen", "rel_sen_abs", "back_link"]
    X = features[feature_cols]
    y = features.positive.astype('int')
    if len(np.unique(y)) <= 1:
        return 1.0
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)
    # print(prop_name, callback)
    clf = callback()
    clf = clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    # print("Ratio de aciertos:", metrics.accuracy_score(y_test, y_pred))
    return metrics.accuracy_score(y_test, y_pred)

def map_bool_to_integer(dataframe, target_cols):
    for i in range(len(dataframe)):
        for col_name in target_cols:
            dataframe.at[i, col_name] = 1 if dataframe.at[i, col_name] == 'True' else 0

def evaluate_models(callbacks, properties, dataframe):

    for a_model_callback in callbacks:
        model_avg = 0
        prop_count = 0
        over_09 = 0
        over_09_avg = 0
        for a_prop in properties:
            filter = dataframe['prop'] == a_prop
            acc = evaluate_prop(prop_name=a_prop,
                                features=dataframe[filter],
                                callback=a_model_callback)
            if acc:
                prop_count += 1
                model_avg += acc
                if acc >= 0.9:
                    over_09 += 1
                    over_09_avg += acc
        print("-----------")
        print(str(a_model_callback),":")
        print("Avg accuracy:", model_avg/prop_count)
        print("Total props over 0.9:", over_09)
        print("Props over 0.9 accuracy:", over_09_avg / over_09)




def run():
    path_to_features = r"F:\datasets\300from200_row_features.csv"

    col_names = ["prop", "instance", "mention", "positive", "direct", "cand_abs",
             "cand_sen", "rel_cand_abs", "rel_cand_sen", "ent_sen", "rel_ent_a",
             "rel_ent_sen", "rel_sen_abs", "back_link"]

    features = pd.read_csv(path_to_features, header=None, names=col_names, sep=";")
    map_bool_to_integer(dataframe=features, target_cols=['positive', 'direct', 'back_link'])

    callbacks = [decission_tree,
                 svc,
                 random_forest,
                 naive_bayes,
                 logistic_reg,
                 k_nearest,
                 neural_netwrok]
    properties = set(features['prop'])

    evaluate_models(callbacks=callbacks,
                    properties=properties,
                    dataframe=features)


if __name__ == "__main__":
    run()

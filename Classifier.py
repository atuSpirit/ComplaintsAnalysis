import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
import pickle

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def load_data(csv_file):
    """Load the feature and label csv file"""
    df = pd.read_csv(csv_file)

    return df


def prepare_data(df):
    """Generate training and test data. one hot coding for categorical columns. Scale
    real value columns using MinMaxScaler. """
    X = df.loc[:, "corpus_score_sum":"company_response"]
    y = df["dispute"]

    old_column_num = len(X.columns)

    # One hot coding for category data
    X = pd.get_dummies(X)
    #print(X.columns)

    # Get the new columns increased by one hot coding. Prepare to add to data to be predicted
    new_column_names = []
    for i in np.arange(old_column_num - 1, len(X.columns)):
        new_column_names.append(X.columns[i])
    #print(new_column_names)

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)

    # Scale the data, only scale word_num and sentence_num because the other column value
    # are in range of [-1, 1] TODO: consider better scale
    scaler = MinMaxScaler()
    scaler.fit(X_train.loc[:, ["word_num", "sentence_num"]])

    X_train.loc[:, ["word_num", "sentence_num"]] = scaler.transform(X_train.loc[:, ["word_num", "sentence_num"]])
    X_test.loc[:, ["word_num", "sentence_num"]] = scaler.transform(X_test.loc[:, ["word_num", "sentence_num"]])
    print(X_test.head())

    # Save the new column names to a file
    column_name_file = "result/column_names.csv"
    with open(column_name_file, "w") as fobj:
        fobj.write(",".join(new_column_names))

    return X_train, X_test, y_train, y_test


def model_evaluate(model, X_train, y_train, X_test, y_test):
    """Evaluate model by accuracy, confusion matrix and f1 score"""
    pred_model = model.predict(X_test)
    print("training score: {:.2f}".format(model.score(X_train, y_train)))
    print("test score: {:.2f}".format(model.score(X_test, y_test)))
    confusion = confusion_matrix(y_test, pred_model)
    print("Confusion matrix:\n{}".format(confusion))
    print("f1 score: {:.2f}".format(f1_score(y_test, pred_model)))


def best_logistic_model(X_train, y_train):
    param_grid = {'C': [0.01, 0.1, 1, 10]}
    grid = GridSearchCV(LogisticRegression(solver="lbfgs", max_iter = 2000), param_grid, cv=5)
    grid.fit(X_train, y_train)
    print(grid.best_params_)
    # print("Best C parameter: {:.2f}".format(grid.best_params_))
    print("Best cross-validation score: {:.2f}".format(grid.best_score_))

    return grid.best_estimator_


def train_model():
    feature_file = "data/complaints.sentiment_data.csv"
    df = load_data(feature_file)
    X_train, X_test, y_train, y_test = prepare_data(df)

    """
    print("Logistic model result")
    lgreg = best_logistic_model(X_train, y_train)
    model_evaluate(lgreg, X_train, y_train, X_test, y_test)

    """
    print("Random Forest result")
    forest = RandomForestClassifier(n_estimators=100, random_state=0)
    forest.fit(X_train, y_train)
    model_evaluate(forest, X_train, y_train, X_test, y_test)

    """
    print("Random Forest result, max_depth: ", depth)
    forest = RandomForestClassifier(n_estimators=200, max_depth = depth, random_state=0)
    forest.fit(X_train, y_train)
    model_evaluate(forest, X_train, y_train, X_test, y_test)
    """
    # Save the model to file
    file_name = "result/finalized_model.sav"
    # pickle.dump(lgreg, open(file_name, 'wb'))
    pickle.dump(forest, open(file_name, 'wb'))

    return


train_model()
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def load_complaints_data(complaints_file):
    complaints = pd.read_csv(complaints_file)
    print("There are {} complaints with narrative ".format(len(complaints)))
    #Discard those data contains no label
    complaints = complaints.dropna(subset=["Consumer disputed?"])

    return complaints


def transfer_label_column(label_column):
    label_column = label_column.apply(lambda x : 1 if x == "Yes" else 0)# for x in label_column)
    #print(label_column)

    #label_column = pd.Series(np.arange(10))
    return label_column


def generate_sentiment_metric(complaints):
    """Generate features from narrative sentiment characteristics, say sentiment of the copus,
        the sentence number of the corpus, word number"""
    corpus_score_list = []
    word_num_list = []
    sentence_num_list = []
    corpus_score_sum_list = []
    negative_ratio_list = []  # The ratio of sentences with negative score in the corpus
    most_negative_score_list = []

    """Initialize Vader sentiment analyzer"""
    analyser = SentimentIntensityAnalyzer()
    stop_words = set(stopwords.words('english'))

    X = pd.DataFrame()

    i = 0
    for narrative in complaints["Consumer complaint narrative"]:
        i += 1
        if i % 1000 == 0:
            print(i)
        sentence_list = sent_tokenize(narrative)
        sentence_score_list = []
        word_num = 0
        copus_score_sum = 0
        negative_num = 0
        most_negative_score = 0

        """Generate sentiment score for each sentence in the narrative"""
        for sentence in sentence_list:
            sentiment_score_dict = analyser.polarity_scores(sentence)
            score = sentiment_score_dict["compound"]  # Use the compound score
            copus_score_sum += score
            word_num += len(word_tokenize(sentence))
            sentence_score_list.append(score)
            if score < -0.05:
                negative_num += 1
            if score < most_negative_score:
                most_negative_score = score

        corpus_score_list.append(sentence_score_list)
        sentence_num_list.append(len(sentence_score_list))
        word_num_list.append(word_num)
        corpus_score_sum_list.append(copus_score_sum)
        negative_ratio_list.append(negative_num / (len(sentence_score_list)))
        most_negative_score_list.append(most_negative_score)

    # Will not use the list as feature
    # X["sentiment_score"] = corpus_score_list
    X["corpus_score_sum"] = corpus_score_sum_list
    X["word_num"] = word_num_list
    X["sentence_num"] = sentence_num_list
    X["negative_ratio"] = negative_ratio_list
    X["most_negative_score"] = most_negative_score_list
    return X

def form_feature_data(complaints):
    X = generate_sentiment_metric(complaints)

    #Add company response in
    X["company_response"] = complaints["Company response to consumer"].reset_index(drop=True)

    #Add the label in
    X["dispute"] = transfer_label_column(complaints["Consumer disputed?"]).reset_index(drop=True)

    return X



def dump_feature_to_csv(data, output_file):
    data.to_csv(output_file, index=False)


def main():
    complaints_file = "data/complaints-2019-05-16_13_17.csv"
    complaints = load_complaints_data(complaints_file)
    X = form_feature_data(complaints)

    output_file = "data/complaints.sentiment_data.csv"
    #dump_feature_to_csv(X, output_file)





#print(X.head())


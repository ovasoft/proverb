import nltk
import random
#from nltk.corpus import movie_reviews
from nltk.classify.scikitlearn import SklearnClassifier
import pickle
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from nltk.classify import ClassifierI
from statistics import mode
from nltk.tokenize import word_tokenize
import os
import sys


class VoteClassifier(ClassifierI):
    def __init__(self, *classifiers):
        self._classifiers = classifiers

    def classify(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)
        return mode(votes)

    def confidence(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)

        choice_votes = votes.count(mode(votes))
        conf = choice_votes / len(votes)
        return conf

dd = os.path.dirname(__file__)
documents_f = open("{}/pickled_algos/documents.pickle".format(dd), "rb")
documents = pickle.load(documents_f)
documents_f.close()




word_features5k_f = open("{}/pickled_algos/word_features5k.pickle".format(dd), "rb")
word_features = pickle.load(word_features5k_f)
word_features5k_f.close()


def find_features(document):
    words = word_tokenize(document)
    features = {}
    for w in word_features:
        features[w] = (w in words)

    return features



#featuresets_f = open("pickled_algos/featuresets.pickle", "rb")
#featuresets = pickle.load(featuresets_f)
#featuresets_f.close()

#random.shuffle(featuresets)
#print(len(featuresets))

#testing_set = featuresets[10000:]
#training_set = featuresets[:10000]



open_file = open("{}/pickled_algos/originalnaivebayes5k.pickle".format(dd), "rb")
classifier = pickle.load(open_file)
open_file.close()


open_file = open("{}/pickled_algos/MNB_classifier5k.pickle".format(dd), "rb")
MNB_classifier = pickle.load(open_file)
open_file.close()



open_file = open("{}/pickled_algos/BernoulliNB_classifier5k.pickle".format(dd), "rb")
BernoulliNB_classifier = pickle.load(open_file)
open_file.close()


open_file = open("{}/pickled_algos/LogisticRegression_classifier5k.pickle".format(dd), "rb")
LogisticRegression_classifier = pickle.load(open_file)
open_file.close()


open_file = open("{}/pickled_algos/LinearSVC_classifier5k.pickle".format(dd), "rb")
LinearSVC_classifier = pickle.load(open_file)
open_file.close()


open_file = open("{}/pickled_algos/SGDC_classifier5k.pickle".format(dd), "rb")
SGDC_classifier = pickle.load(open_file)
open_file.close()




voted_classifier = VoteClassifier(
                                  classifier,
                                  LinearSVC_classifier,
                                  MNB_classifier,
                                  BernoulliNB_classifier,
                                  LogisticRegression_classifier)




def sentiment(text):
    feats = find_features(text)
    return MNB_classifier.classify(feats)

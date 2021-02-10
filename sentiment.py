from nltk.tokenize import sent_tokenize, word_tokenize
import pyhmeter
import re
from heapq import nlargest, nsmallest
from operator import itemgetter
from nltk.sentiment import SentimentIntensityAnalyzer

def getPyhmeter(tweet_text):
    #TODO: remove URL and other stuff to clean text
    pattern = re.compile('(@\w*)|(\|.*)')
    removedAt = pattern.sub('', tweet_text)
    tokens = word_tokenize(removedAt)
    # TODO Language according to tweet, and load file external
    file = pyhmeter.load_scores("Hedonometer.csv")
    return pyhmeter.HMeter(tokens, file, 1)

def getHapinessScore(tweet_text):
    pyhmeter = getPyhmeter(tweet_text)
    score = pyhmeter.happiness_score()
    if score == None :
        return -1
    else:
        return score

def getWordsWithScoere(tweet_text):
    pyhmeter = getPyhmeter(tweet_text)
    return pyhmeter.matchValueList

def nltksen():
    sia = SentimentIntensityAnalyzer()
    print(sia.polarity_scores("Wow, NLTK is really powerful but also kinda not you terrorist bad horrible death rape murder!"))


print(getHapinessScore("Wow, NLTK is really powerful but also kinda not you terrorist bad horrible death rape murder!"))

nltksen()
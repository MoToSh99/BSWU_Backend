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
    if len(tokens) < 10:
      return -1
    # TODO Language according to tweet, and load file external
    file = pyhmeter.load_scores("Hedonometer.csv")
    return pyhmeter.HMeter(tokens, file, 1)

def getHapinessScore(tweet_text):
    pyhmeter = getPyhmeter(tweet_text)
    if(pyhmeter == -1):
        return -1
   
    score = pyhmeter.happiness_score()
    if score == None :
        return -1
    else:
        return score

def getWordsWithScoere(tweet_text):
    pyhmeter = getPyhmeter(tweet_text)
    if(pyhmeter == -1):
        return []
    else:
        return pyhmeter.matchValueList

def nltksen():
    sia = SentimentIntensityAnalyzer()
    print(sia.polarity_scores("Hallo, how are you today 👹"))

def rescale(X,A,B,C,D,force_float=False):
    retval = ((float(X - A) / (B - A)) * (D - C)) + C
    if not force_float and all(map(lambda x: type(x) == int, [X,A,B,C,D])):
        return int(round(retval))
    return retval

print(rescale(0.75, -1, 1, 1, 9))

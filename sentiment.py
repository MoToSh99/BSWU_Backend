from nltk.tokenize import TweetTokenizer
import pyhmeter
import re
from heapq import nlargest, nsmallest
from operator import itemgetter

def getPyhmeter(tweet_text):
    #TODO: remove URL and other stuff to clean text
    pattern = re.compile('(@\w*)|(\|.*)|(#\s*)')
    removedAt = pattern.sub('', tweet_text)
    tk = TweetTokenizer()
    tokens = tk.tokenize(removedAt)
    file = pyhmeter.load_scores()
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

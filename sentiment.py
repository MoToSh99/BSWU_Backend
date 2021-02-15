from nltk.tokenize import TweetTokenizer
import pyhmeter
import re
from heapq import nlargest, nsmallest
from operator import itemgetter
import time


file = pyhmeter.load_scores()

# Gets the Pyhmeter and removes unnecessary symbols from a given tweet
def getPyhmeter(tweet_text):
    #TODO: remove URL and other stuff to clean text
    pattern = re.compile('(@\w*)|(\|.*)|(#\s*)')
    removedAt = pattern.sub('', tweet_text)
    tk = TweetTokenizer()
    tokens = tk.tokenize(removedAt)
    return pyhmeter.HMeter(tokens, file, 1)

# Gets the happiness score from a single tweet
def getScores(tweet_text):
    pyhmeter = getPyhmeter(tweet_text)
    hapinessScore = pyhmeter.happiness_score()
    # Get all matches from a single tweet along with their individual scores
    wordScore = pyhmeter.matchValueList
    if hapinessScore == None :
        return -1, -1
    else:
        return hapinessScore, wordScore



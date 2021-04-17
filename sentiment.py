from nltk.tokenize import TweetTokenizer
import pyhmeter
import re
from heapq import nlargest, nsmallest
from operator import itemgetter

file = pyhmeter.load_scores()

# Gets the Pyhmeter and removes unnecessary symbols from a given tweet
def getPyhmeter(tweet_text):
    #TODO: remove URL and other stuff to clean text
    pattern = re.compile('(@\w*)|(\|.*)|(#\s*)')
    removedAt = pattern.sub('', tweet_text)
    tk = TweetTokenizer()
    tokens = tk.tokenize(removedAt)
    
    return pyhmeter.HMeter(tokens, file, 0)

# Gets the happiness score from a single tweet
def getHapinessScore(tweet_text):
    pyhmeter = getPyhmeter(tweet_text)
    score = pyhmeter.happiness_score()
    if score == None :
        return -1
    else:
        return score 

# Get all matches from a single tweet along with their individual scores
def getWordsWithScore(tweet_text):
    global file
    file = pyhmeter.load_scores_word()
    py = getPyhmeter(tweet_text)
    return py.matchValueList

from nltk.tokenize import TweetTokenizer
import pyhmeter
import re
from heapq import nlargest, nsmallest
from operator import itemgetter

file = pyhmeter.load_scores()
onlyWord = pyhmeter.load_scores_word()

# Gets the Pyhmeter and removes unnecessary symbols from a given tweet
def getPyhmeter(tweet_text):
    #TODO: remove URL and other stuff to clean text
    pattern = re.compile('(@\w*)|(\|.*)|(#\s*)')
    removedAt = pattern.sub('', tweet_text)
    tk = TweetTokenizer()
    tokens = tk.tokenize(removedAt)
    
    return pyhmeter.HMeter(tokens, file, onlyWord,  1)

# Gets the happiness score from a single tweet
def getHapinessScore(tweet_text):
    pyhmeter = getPyhmeter(tweet_text)
    score = pyhmeter.happiness_score()
    if score == None :
        return -1, -1
    else:
        return score, pyhmeter.matchValueList
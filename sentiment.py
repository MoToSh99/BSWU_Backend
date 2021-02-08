from nltk.tokenize import sent_tokenize, word_tokenize
import pyhmeter
import re
from heapq import nlargest, nsmallest
from operator import itemgetter

def getHapinessScore(tweet_text):
    #TODO: remove URL and other stuff to clean text
    pattern = re.compile('@\w*')
    removedAt = pattern.sub('', tweet_text)
    tokens = word_tokenize(removedAt)
    # TODO Language according to tweet, and load file external
    file = pyhmeter.load_scores("Hedonometer.csv")
    h = pyhmeter.HMeter(tokens, file, 1)
    score = h.happiness_score()
    if score == None :
        return -1
    else:
        return score


def happyWords(text):
    #TODO: remove URL and other stuff to clean text
    pattern = re.compile('@\w*')
    removedAt = pattern.sub('', text)
    tokens = word_tokenize(removedAt)
    # TODO Language according to tweet, and load file external
    file = pyhmeter.load_scores("Hedonometer.csv")
    h = pyhmeter.HMeter(tokens, file, 1)
    wordsmatched = h.matchlist
    return h.matchValueList
    #res = nlargest(5, w, key=w.get)
    #ress = nsmallest(5, w, key=w.get)
    



        
happyWords()
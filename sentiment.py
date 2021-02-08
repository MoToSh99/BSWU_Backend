from nltk.tokenize import sent_tokenize, word_tokenize
import pyhmeter
import re

def getHapinessScore(tweet_text):
    #TODO: remove URL and other stuff to clean text
    pattern = re.compile('@\w*')
    removedAt = pattern.sub('', tweet_text)
    tokens = word_tokenize(removedAt)
    # TODO Language according to tweet, and load file external
    file = pyhmeter.load_scores("Hedonometer.csv")
    h = pyhmeter.HMeter(tokens, file, 1)
    score = h.happiness_score()
    if score== None :
        return -1
    else:
        return score



        
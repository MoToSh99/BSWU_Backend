from nltk.tokenize import TweetTokenizer
import pyhmeter
import re
from heapq import nlargest, nsmallest
from operator import itemgetter
import config
import tweepy as tw
import pandas as pd

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
def getHapinessScore(tweet_text):

    global file
    file = pyhmeter.load_scores()
    py = getPyhmeter(tweet_text)
    score = py.happiness_score()


    file = pyhmeter.load_scores_word()
    py2 = getPyhmeter(tweet_text)
    score2 = py2.happiness_score()

    file = pyhmeter.load_scores_emoji()
    py3 = getPyhmeter(tweet_text)
    score3 = py2.happiness_score()

    
    if score != None and score2 != None and len(py3.matchlist) != 0 :
        #print("Full Text: " + tweet_text)
        #print ("With emoji")
        #print(py.matchlist)
        #print(score)

        #print("Without emoji")
        #print(py2.matchlist)
        #print(score2)
        #print("\n")

        return  score2
    
    return  -1
        

    


# Get all matches from a single tweet along with their individual scores
def getWordsWithScore(tweet_text):
    pyhmeter = getPyhmeter(tweet_text)
    return pyhmeter.matchValueList


def randomTweets():
    api = config.setupTwitterAuth()
    places = api.geo_search(query="USA", granularity="country")
    place_id = places[0].id
    tweets = tw.Cursor(api.search, q="place:%s" % place_id, tweet_mode='extended', lang='en').items(3100)
    score = {}
    
        
    for t in tweets:
        score = getHapinessScore(t.full_text)
        if score != -1:
            print(str(score) + ",")
    

#df = pd.DataFrame.from_dict(randomTweets(), orient="index" )
#df.to_csv("data.csv")
randomTweets()

from nltk.tokenize import TweetTokenizer
import pyhmeter
import re
from heapq import nlargest, nsmallest
from operator import itemgetter
import config
import tweepy as tw
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from scipy.stats import kde
import seaborn as sns

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
def getHapinessScoreTextWithEmoji(tweet_text):

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
        #print(tweet_text)
        return  score
    
    return  -1

def TweetsgetHapinessScoreTextWithEmoji():
    api = config.setupTwitterAuth()
    places = api.geo_search(query="USA", granularity="country")
    place_id = places[0].id
    tweets = tw.Cursor(api.search, q="place:%s" % place_id, tweet_mode='extended', lang='en').items(100)        
    tweetss = {}
    count = 1

    for tweet in tweets:
        score = getHapinessScoreTextWithEmoji(tweet.full_text)
        if score != -1:
            dict = { count : {"id" : tweet.id, "score" : score, "created" : str(tweet.created_at) }}
            tweetss.update(dict)
            count += 1

    return tweetss
    

def putEmojiData1():
    engine = create_engine('postgres://efkgjaxasehspw:7ebb68899129ff95e09c3000620892ac7804d150083b80a3a8fc632d1ab250cb@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/dfnb8s6k7aikmo')
    api = config.setupTwitterAuth()
    df = pd.DataFrame.from_dict(TweetsgetHapinessScoreTextWithEmoji(), orient='index')
    df.set_index('id', inplace=True)
    df.to_sql('emoji_textwithemoji', con=engine, if_exists='append')

    engine.execute("DELETE FROM emoji_textwithemoji T1 USING emoji_textwithemoji T2 WHERE  T1.ctid  < T2.ctid AND  T1.id    = T2.id AND  T1.score = T2.score AND  T1.created = T2.created;")
  
    read  = pd.read_sql("emoji_textwithemoji", con=engine) 

def getHapinessScoreTextWithEmojiRemoved(tweet_text):

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
        #print(tweet_text)
        return  score2
    
    return  -1

def TweetsgetHapinessScoreTextWithEmojiRemoved():
    api = config.setupTwitterAuth()
    places = api.geo_search(query="USA", granularity="country")
    place_id = places[0].id
    tweets = tw.Cursor(api.search, q="place:%s" % place_id, tweet_mode='extended', lang='en').items(100)        
    tweetss = {}
    count = 1

    for tweet in tweets:
        score = getHapinessScoreTextWithEmojiRemoved(tweet.full_text)
        if score != -1:
            dict = { count : {"id" : tweet.id, "score" : score, "created" : str(tweet.created_at) }}
            tweetss.update(dict)
            count += 1

    return tweetss
    

def putEmojiData2():
    engine = create_engine('postgres://efkgjaxasehspw:7ebb68899129ff95e09c3000620892ac7804d150083b80a3a8fc632d1ab250cb@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/dfnb8s6k7aikmo')
    api = config.setupTwitterAuth()
    df = pd.DataFrame.from_dict(TweetsgetHapinessScoreTextWithEmojiRemoved(), orient='index')
    df.set_index('id', inplace=True)
    df.to_sql('emoji_textwithemojiremoved', con=engine, if_exists='append')

    engine.execute("DELETE FROM emoji_textwithemojiremoved T1 USING emoji_textwithemojiremoved T2 WHERE  T1.ctid  < T2.ctid AND  T1.id    = T2.id AND  T1.score = T2.score AND  T1.created = T2.created;")
  
    read  = pd.read_sql("emoji_textwithemojiremoved", con=engine) 

def getHapinessScoreTextWithOutEmoji(tweet_text):

    global file
    file = pyhmeter.load_scores()
    py = getPyhmeter(tweet_text)
    score = py.happiness_score()

    file = pyhmeter.load_scores_emoji()
    py3 = getPyhmeter(tweet_text)

    if score != None and len(py3.matchlist) == 0 :
        #print(tweet_text)
        return  score
    
    return  -1


def TweetsgetHapinessScoreTextWithOutEmoji():
    api = config.setupTwitterAuth()
    places = api.geo_search(query="USA", granularity="country")
    place_id = places[0].id
    tweets = tw.Cursor(api.search, q="place:%s" % place_id, tweet_mode='extended', lang='en').items(100)        
    tweetss = {}
    count = 1

    for tweet in tweets:
        score = getHapinessScoreTextWithOutEmoji(tweet.full_text)
        if score != -1:
            dict = { count : {"id" : tweet.id, "score" : score, "created" : str(tweet.created_at) }}
            tweetss.update(dict)
            count += 1

    return tweetss
    

def putEmojiData3():
    engine = create_engine('postgres://efkgjaxasehspw:7ebb68899129ff95e09c3000620892ac7804d150083b80a3a8fc632d1ab250cb@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/dfnb8s6k7aikmo')
    api = config.setupTwitterAuth()
    df = pd.DataFrame.from_dict(TweetsgetHapinessScoreTextWithOutEmoji(), orient='index')
    df.set_index('id', inplace=True)
    df.to_sql('emoji_textwithoutemoji', con=engine, if_exists='append')

    engine.execute("DELETE FROM emoji_textwithoutemoji T1 USING emoji_textwithoutemoji T2 WHERE  T1.ctid  < T2.ctid AND  T1.id    = T2.id AND  T1.score = T2.score AND  T1.created = T2.created;")
  
    read  = pd.read_sql("emoji_textwithoutemoji", con=engine) 



def putEmojiData():
    putEmojiData1()
    putEmojiData2()
    putEmojiData3()

putEmojiData()

def createHistogram():  
    engine = create_engine('postgres://efkgjaxasehspw:7ebb68899129ff95e09c3000620892ac7804d150083b80a3a8fc632d1ab250cb@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/dfnb8s6k7aikmo')  
    read  = pd.read_sql("emoji_textwithoutemoji", con=engine) 
    data = list(read["score"])

    plt.hist(data, density=True, bins=5)  # density=False would make counts
    plt.ylabel('Frequency')
    plt.xlabel('Sentiment score')

    plt.show()

def createDensityPlot():
    engine = create_engine('postgres://efkgjaxasehspw:7ebb68899129ff95e09c3000620892ac7804d150083b80a3a8fc632d1ab250cb@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/dfnb8s6k7aikmo')  
    #read  = pd.read_sql("emoji_textwithemoji", con=engine)
    read2  = pd.read_sql("emoji_textwithoutemoji", con=engine) 

    #data = list(read["score"])
    data2 = list(read2["score"])

    #sns.kdeplot(data, color="green", shade=True)
    sns.kdeplot(data2, color="blue", shade=True)
    #plt.show()
    plt.show()

#createHistogram()
#createDensityPlot()
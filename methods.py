import tweepy as tw
from tweepy.models import User
from tweepy.error import TweepError
import config
import re
import sentiment
import operator
from heapq import nlargest, nsmallest
import time
import datetime
import numpy as np
from sqlalchemy import create_engine
import pandas as pd
import json

# Returns all relevant data to the API
def getData(username, count):
    # Set up Twitter API
    api = config.setupTwitterAuth()
    print("Count: " + str(count))
    tic = time.perf_counter()
    allTweets = tw.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended", exclude_replies=False, include_rts=False, lang='en').items(count)
    listAllTweets = list(allTweets)
    toc = time.perf_counter()
    print(f"Downloaded data in {toc - tic:0.4f} seconds")
    tic2 = time.perf_counter()
    tweetsDict = getTweetsDict(listAllTweets)
    tweetsOnlyScores = tweetsOnlyScore(tweetsDict)
    wordsAmount, topWords = getTopFiveWords(listAllTweets)
    overallScore = getOverallScore(tweetsDict)
    data = {
     "userinfo" : getProfileInfo(username),
     "overallscore" : overallScore,
     "tweets" : { "happiest" : getHappiestTweet(tweetsOnlyScores), "saddest" : getSaddestTweet(tweetsOnlyScores) },
     "alltweets" : tweetsDict,
     "topfivewords" : topWords,
     "wordsmatched" : wordsAmount,
     "weekscores" : getWeekScores(tweetsDict),
     "tweetstart" :  tweetsDict[len(tweetsDict)-1]["created"],
     "tweetsamount" : len(tweetsDict),
     "celebrityscore" : getClosestsCelebrities(overallScore)
    }

    toc2 = time.perf_counter()
    print(f"Done in {toc2 - tic:0.4f} seconds")
    
    return data

# Get all tweets and collect them in a dictionary
def getTweetsDictRaw(allTweets):
    tic = time.perf_counter()
    tweets = {}
    count = 1
    for tweet in allTweets:
        score = sentiment.getHapinessScore(tweet.full_text)
        if score != -1:
            dict = { count : {"id" : tweet.id, "score" : score, "created" : str(tweet.created_at) }}
            tweets.update(dict)
            count += 1
    toc = time.perf_counter()
    print(f"getTweetsDict in {toc - tic:0.4f} seconds")       
    return tweets

def getTweetsDict(allTweets):
    df = pd.DataFrame.from_dict(getTweetsDictRaw(allTweets), orient='index')    
    result = df.to_json(orient="records")
    parsed = json.loads(result)
    return parsed


# Get the top five happiest and unhappiest words used by the user
def getTopFiveWords(allTweets):
    tic = time.perf_counter()
    
    wordDict = {}
    for tweet in allTweets:
        wordDict.update(sentiment.getWordsWithScore(tweet.full_text))
    
    toc = time.perf_counter()

    print(f"getTopFiveWords in {toc - tic:0.4f} seconds")
    return len(wordDict), {"top" : nlargest(5, wordDict, key=wordDict.get), "bottom" : nsmallest(5, wordDict, key=wordDict.get)}

#TODO Evt. fix måden at få data på
# Only get tweet id's and scores
def tweetsOnlyScore(scores):
    tic = time.perf_counter()
    
    scoresOnly = {}
    for score in scores:
        dict = {score["id"] : score["score"]}
        scoresOnly.update(dict)

    toc = time.perf_counter()
    print(f"tweetsOnlyScore in {toc - tic:0.4f} seconds")
    
    return scoresOnly

# Get profile info from user
def getProfileInfo(username):
    tic = time.perf_counter()

    api = config.setupTwitterAuth()

    try:
        user = api.get_user(username)
    except TweepError as e:
        return e
        
    # Remove _normal from profile image URL
    profile_image_url = user.profile_image_url_https
    url = re.sub('_normal', '', profile_image_url)
    userInfo = {
        "name" : user.name,
        "username" : user.screen_name,
        "location" : str(user.location),
        "profile_location" : str(user.profile_location),
        "geo_enabled" : user.geo_enabled,
        "statuses_count" : user.statuses_count,
        "followers_count" : user.followers_count,
        "friends_count" : user.friends_count,
        "verified" : user.verified,
        "profile_image_url" : url
    }

    toc = time.perf_counter()
    print(f"getProfileInfo in {toc - tic:0.4f} seconds")
    return userInfo

# Get the happiest tweet posted by the user. Returns the id of the tweet.
def getHappiestTweet(scores): 
    tic = time.perf_counter()
    

    tweet = max(scores.items(), key=operator.itemgetter(1))[0]
    score = max(scores.items(), key=operator.itemgetter(1))[1]
    id = str(tweet)


    toc = time.perf_counter()
    print(f"getHappiestTweet in {toc - tic:0.4f} seconds")
     
    return {"id" : id, "score" : score}

# Get the unhappiest tweet posted by the user. Returns the id of the tweet.
def getSaddestTweet(scores):
    tic = time.perf_counter()
    
    tweet = min(scores.items(), key=operator.itemgetter(1))[0]
    score = max(scores.items(), key=operator.itemgetter(1))[1]
    id = str(tweet)

    toc = time.perf_counter()
    print(f"getSaddestTweet in {toc - tic:0.4f} seconds")
    
    return {"id" : id, "score" : score}

# Get the overall happiness score from a collection of tweets
def getOverallScore(tweetsDict):
    tic = time.perf_counter()

    total = 0
    count = 0
    for tweet in tweetsDict:
        total += tweet["score"]
        count += 1

    toc = time.perf_counter()
    print(f"getOverallScore in {toc - tic:0.4f} seconds")

    return float("{:.2f}".format(total/count))

# Get the average scores distributed over individual weekdays
def getWeekScores(tweetsDict):
    tic = time.perf_counter()
    weekdays = [0, 0, 0, 0, 0, 0, 0]
    weekdayScores = [0, 0, 0, 0, 0, 0, 0]
    for tweet in tweetsDict:
        dt = tweet["created"]
        date = dt.split(' ')
        part = date[0]
        year, month, day = (int(x) for x in part.split('-'))   
        ans = datetime.date(year, month, day)

        weekdays[ans.weekday()] += 1
        weekdayScores[ans.weekday()] += tweet["score"]
    
    np.seterr(divide='ignore', invalid='ignore')
    out = np.divide(weekdayScores, weekdays)
    withoutNan = np.nan_to_num(out) 
    toc = time.perf_counter()
    print(f"getWeekScores in {toc - tic:0.4f} seconds")

    return list(withoutNan)

# Get the closest three scores from a list of chosen celebrities on Twitter
def getClosestsCelebrities(overallScore):
    engine = create_engine('postgres://fptgchibpcgsug:82c819e919e1b13f7e80f667ac1ddbc0eb85747a59a3360ab77175992f88eb2d@ec2-52-209-134-160.eu-west-1.compute.amazonaws.com:5432/dermsjvi46fmof')
    celebScores  = pd.read_sql("celebrity", con=engine)

    df_sort = celebScores.iloc[(celebScores['score']-overallScore).abs().argsort()[:3]]
    
    result = df_sort.to_json(orient="records")
    parsed = json.loads(result)
    return parsed

#getData("STANN_co", 100)

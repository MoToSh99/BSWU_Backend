import tweepy as tw
from tweepy.models import User
import config
import re
import sentiment
import operator
from heapq import nlargest, nsmallest
import time

# Returns all relevant data to the API
def getData(username):
    # Set up Twitter API
    api = config.setupTwitterAuth()
    count = 100
    print("Count: " + str(count))
    tic = time.perf_counter()
    allTweets = tw.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended", exclude_replies=False, include_rts=False, lang='en').items(count)
    listAllTweets = list(allTweets)
    toc = time.perf_counter()
    print(f"Downloaded data in {toc - tic:0.4f} seconds")
    tic2 = time.perf_counter()
    tweetsDict = getTweetsDict(listAllTweets)
    tweetsOnlyScores = tweetsOnlyScore(tweetsDict)
    data = {
     "userinfo" : getProfileInfo(username),
     "overallscore" : getOverallScore(tweetsDict),
     "tweets" : { "happiest" : getHappiestTweet(tweetsOnlyScores), "saddest" : getSaddestTweet(tweetsOnlyScores) },
     "alltweets" : tweetsDict,
     "topfivewords" : getTopFiveWords(listAllTweets),
    }

    toc2 = time.perf_counter()
    print(f"Done in {toc2 - tic:0.4f} seconds")
    
    return data


# Get all tweets and collect them in a dictionary
def getTweetsDict(allTweets):
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

# Get the top five happiest and unhappiest words used by the user
def getTopFiveWords(allTweets):
    tic = time.perf_counter()
    
    wordDict = {}
    for tweet in allTweets:
        wordDict.update(sentiment.getWordsWithScore(tweet.full_text))
    
    toc = time.perf_counter()

    print(f"getTopFiveWords in {toc - tic:0.4f} seconds")
    return {"top" : nlargest(5, wordDict, key=wordDict.get), "bottom" : nsmallest(5, wordDict, key=wordDict.get)}

#TODO Evt. fix måden at få data på
# Only get tweet id's and scores
def tweetsOnlyScore(scores):
    tic = time.perf_counter()
    
    scoresOnly = {}
    for score in scores:
        dict = {scores[score]["id"] : scores[score]["score"]}
        scoresOnly.update(dict)

    toc = time.perf_counter()
    print(f"tweetsOnlyScore in {toc - tic:0.4f} seconds")
    
    return scoresOnly

# Get profile info from user
def getProfileInfo(username):
    tic = time.perf_counter()
    
    api = config.setupTwitterAuth()
    user = api.get_user(username) 
    # Remove _normal from profile image URL
    profile_image_url = user.profile_image_url_https
    url = re.sub('_normal', '', profile_image_url)
    userInfo = {
        "name" : user.name,
        "username" : user.screen_name,
        "location" : str(user.location),
        "profile_location" : str(user.profile_location),
        "geo_enabled" : str(user.geo_enabled),
        "followers_count" : str(user.followers_count),
        "friends_count" : str(user.friends_count),
        "verified" : str(user.verified),
        "profile_image_url" : url
    }

    toc = time.perf_counter()
    print(f"getProfileInfo in {toc - tic:0.4f} seconds")
    return userInfo

# Get the happiest tweet posted by the user. Returns the id of the tweet.
def getHappiestTweet(scores): 
    tic = time.perf_counter()
    
    tweet = max(scores.items(), key=operator.itemgetter(1))[0]
    id = str(tweet)

    toc = time.perf_counter()
    print(f"getHappiestTweet in {toc - tic:0.4f} seconds")
     
    return id

# Get the unhappiest tweet posted by the user. Returns the id of the tweet.
def getSaddestTweet(scores):
    tic = time.perf_counter()
    
    tweet = min(scores.items(), key=operator.itemgetter(1))[0]
    id = str(tweet)

    toc = time.perf_counter()
    print(f"getSaddestTweet in {toc - tic:0.4f} seconds")
    
    return id

# Get the overall happiness score from a collection of tweets
def getOverallScore(tweetsDict):
    tic = time.perf_counter()

    total = 0
    count = 0
    for tweet in tweetsDict:
        total += tweetsDict[tweet]["score"]
        count += 1

    toc = time.perf_counter()
    print(f"getOverallScore in {toc - tic:0.4f} seconds")

    return float("{:.2f}".format(total/count))




#getData("STANN_co")

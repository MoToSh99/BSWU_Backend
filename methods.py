import tweepy as tw
from tweepy.models import User
import config
import re
import sentiment
import operator

def getData(username):
    # Set up Twitter API
    api = config.setupTwitterAuth()
    allTweets = tw.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended", exclude_replies=False, include_rts=False).items(10)
    tweetsDict = getTweetsDict(allTweets)

    print(tweetsDict)
    data = {
     "userinfo" : getProfileInfo(username),
     "tweets" : { "happiest" : getHappiestTweet(tweetsOnlyScore(tweetsDict)), "saddest" : getSaddestTweet(tweetsOnlyScore(tweetsDict)) },
     "allTweets" : tweetsDict,
    }
    
    return data

def getTweetsDict(allTweets):
    tweets = {}
    count = 1
    for tweet in allTweets:
        score = sentiment.getHapinessScore(tweet.full_text)
        if score != -1:
            dict = { count : {"id" : tweet.id, "score" : score, "created" : str(tweet.created_at) }}
            tweets.update(dict)
            count += 1
            
    return tweets

def getTopFiveWords(allTweets):
    words = {}
    count = 1
    for tweet in allTweets:
        score = sentiment.getHapinessScore(tweet.full_text)
        if score != -1:
            dict = { count : word}
            tweets.update(dict)
            count += 1
            
    return words

#TODO Evt. fix måden at få data på
def tweetsOnlyScore(scores):
    scoresOnly = {}
    for score in scores:
        dict = {scores[score]["id"] : scores[score]["score"]}
        scoresOnly.update(dict)
    return scoresOnly

# Get profile info from user
def getProfileInfo(username):
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

    return userInfo

def getHappiestTweet(scores): 
    tweet = max(scores.items(), key=operator.itemgetter(1))[0]
    id = str(tweet)
     
    return id

def getSaddestTweet(scores):
    tweet = min(scores.items(), key=operator.itemgetter(1))[0]
    id = str(tweet)
    
    return id


getData("STANN_co")
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

listAllTweets = []

def getTwitterData(username, count):
    # Set up Twitter API
    api = config.setupTwitterAuth()
    tic = time.perf_counter()
    try:
        user = api.get_user(username)
    except TweepError as e:
        print(e)
        return {"Error" : e.args[0][0]['message'] }

    print("Count: " + str(count))
        
    allTweets = tw.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended", exclude_replies=False, include_rts=False, lang='en').items(count)
    listAllTweets = list(allTweets)
    if (len(listAllTweets) == 0):
        return {"Error" : "No tweets"}
    toc = time.perf_counter()
    print(f"Downloaded data in {toc - tic:0.4f} seconds")

    return listAllTweets


# Returns all relevant data to the API
def getData(username):

    tic = time.perf_counter()
    
    engine = create_engine('postgres://efkgjaxasehspw:7ebb68899129ff95e09c3000620892ac7804d150083b80a3a8fc632d1ab250cb@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/dfnb8s6k7aikmo')
    
    tweetsDict = getTweetsDict(listAllTweets)
    dateobject = tweetsDict[len(tweetsDict)-1]["created"]
    formattedDate = formatDate(dateobject)

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
     "tweetstart" :  formattedDate,
     "tweetsamount" : len(tweetsDict),
     "celebrityscore" : getClosestsCelebrities(username, overallScore, engine),
     "danishuserscore" : getDanishUsersScore(overallScore, engine)
    }

    #tweetsByMonth(tweetsDict)

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
     
    return {"id" : id, "score" : float("{:.2f}".format(score))}

# Get the unhappiest tweet posted by the user. Returns the id of the tweet.
def getSaddestTweet(scores):
    tic = time.perf_counter()
    
    tweet = min(scores.items(), key=operator.itemgetter(1))[0]
    score = min(scores.items(), key=operator.itemgetter(1))[1]
    id = str(tweet)

    toc = time.perf_counter()
    print(f"getSaddestTweet in {toc - tic:0.4f} seconds")
    
    return {"id" : id, "score" : float("{:.2f}".format(score))}

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
    withoutNanList = list(withoutNan)

    count = 0
    for score in withoutNanList:
        withoutNan[count] = float("{:.2f}".format(score))
        withoutNanList[count] = float("{:.2f}".format(score))
        count += 1

    toc = time.perf_counter()
    print(f"getWeekScores in {toc - tic:0.4f} seconds")

    weekdayNames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    highestScore = max(withoutNan)
    highestWeekday = weekdayNames[withoutNanList.index(highestScore)]

    np.delete(withoutNan, withoutNanList.index(highestScore))
    weekdayNames.remove(highestWeekday)

    return {
            0 : {"Day" : highestWeekday, "Score" : highestScore}, 
            1 : {"Day" : weekdayNames[0], "Score" : withoutNan[0]},
            2 : {"Day" : weekdayNames[1], "Score" : withoutNan[1]},
            3 : {"Day" : weekdayNames[2], "Score" : withoutNan[2]},
            4 : {"Day" : weekdayNames[3], "Score" : withoutNan[3]},
            5 : {"Day" : weekdayNames[4], "Score" : withoutNan[4]},
            6 : {"Day" : weekdayNames[5], "Score" : withoutNan[5]}
            }

# Get the closest three scores from a list of chosen celebrities on Twitter
def getClosestsCelebrities(username, overallScore, engine):
    celebScores  = pd.read_sql("celebrity", con=engine)
    celebScores = celebScores.drop(celebScores[(celebScores['username']==username)].index)

    df_sort = celebScores.iloc[(celebScores['score']-overallScore).abs().argsort()[:3]]
    
    result = df_sort.to_json(orient="records")
    parsed = json.loads(result)
    return parsed

# Get date as string containing month and day with correct suffix
def formatDate(date):
    date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    day = date.day

    if (3 < day < 21) or (23 < day < 31):
        day = str(day) + 'th'
    else:
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        day = str(day) + suffixes[day % 10]

    datestring = date.strftime("%B " + str(day) + " %Y")
    return datestring

def tweetsByMonth(tweetsDict):   
    months = {
        1:{"score": 0, "amount": 0, "avg":0},
        2:{"score": 0, "amount": 0, "avg":0},
        3:{"score": 0, "amount": 0, "avg":0},
        4:{"score": 0, "amount": 0, "avg":0},
        5:{"score": 0, "amount": 0, "avg":0},
        6:{"score": 0, "amount": 0, "avg":0},
        7:{"score": 0, "amount": 0, "avg":0},
        8:{"score": 0, "amount": 0, "avg":0},
        9:{"score": 0, "amount": 0, "avg":0},
        10:{"score": 0, "amount": 0, "avg":0},
        11:{"score": 0, "amount": 0, "avg":0},
        12:{"score": 0, "amount": 0, "avg":0}
        }
    tweets : typing.Dict[int, months] = {}

    for tweet in tweetsDict:
        dt = tweet["created"]
        date = dt.split(' ')
        part = date[0]
        year, month, day = (int(x) for x in part.split('-')) 
        ans = datetime.date(year, month, day)
        dict = {ans.month :  {"score" : months[ans.month]['score'] + tweet["score"], "amount" : months[ans.month]['amount'] + 1, "avg" : (months[ans.month]['score'] + tweet["score"])/(months[ans.month]['amount'] + 1)}}
        months.update(dict)
        tweets.update({ans.year : months})
    
    print(tweets)

    return tweets

# Get the closest three scores from a list of chosen celebrities on Twitter
def getDanishUsersScore(overallScore,engine ):
    df = pd.read_sql("danishusers", con=engine)
    df_sort = df.sort_values(by=['score'])
    
    danishOverall = float("{:.2f}".format(df_sort["score"].mean()))
    amountOfUsers = len(df_sort.index)

    over = len(df_sort[(df_sort['score']>overallScore)])
    under = len(df_sort[(df_sort['score']>overallScore)])

    percent = float("{:.2f}".format(over/len(df_sort)*100))


    return {"danishoverall" : danishOverall, "usersamount" : amountOfUsers, "usersless" : under, "percent" : percent}

# Get the users that the given user follows
def userFollowers(username, api):
    friends = tw.Cursor(api.friends, screen_name=username).items(200)
    for friend in friends: 
        print(friend.screen_name)

#getData("robysinatra", 50)
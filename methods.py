from sqlalchemy.sql.expression import over
import tweepy as tw
from tweepy.models import User
from tweepy.error import TweepError
import config as c
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
import math
from decouple import config

debug = False
lastDate = datetime.datetime.now()

# Returns all relevant data to the API
def getData(username, count):
    global lastDate

    # Set up Twitter API
    api = c.setupTwitterAuth()

    tic = time.perf_counter()

    print("Count: " + str(count))

    tweets = api.user_timeline(screen_name=username, exclude_replies=False, include_rts = False, lang="en", tweet_mode = 'extended', count=200)
    alltweets = []
    alltweets.extend(tweets)
    oldest = tweets[-1].id

    while len(alltweets) < count:
        tweets = api.user_timeline(screen_name=username, exclude_replies=False, include_rts = False, lang="en", tweet_mode = 'extended', count=200, max_id = oldest - 1)
        if len(tweets) == 0:
            break
        oldest = tweets[-1].id
        alltweets.extend(tweets)

    debugPrint(f"{len(alltweets)} Tweets downloaded")

    try:
        user = api.get_user(username)
    except TweepError as e:
        print(e)
        return {"Error" : e.args[0][0]['message'] }
 
    if (len(alltweets) == 0):
        return {"Error" : "No tweets"}

    toc = time.perf_counter()
    print(f"Downloaded data in {toc - tic:0.4f} seconds")

    listAllTweets = {username : alltweets}

    if (username not in listAllTweets):
        return {"Error" : True}
    tic = time.perf_counter()

    engine = create_engine(config('POSTGRESS'))
    
    tweets = listAllTweets[username]
    tweetsDict, wordDict = getTweetsDict(tweets)
    tweetsOnlyScores = tweetsOnlyScore(tweetsDict)
    
    userinfo = getProfileInfo(username)
    overallScore = getOverallScore(tweetsDict)
    topWords = {"top" : nlargest(5, wordDict, key=wordDict.get), "bottom" : nsmallest(5, wordDict, key=wordDict.get)}
    wordsAmount = len(wordDict)
    highest, lowest, week = getWeekScores(tweetsDict)
    dateobjectEaliest = tweetsDict[len(tweetsDict)-1]["created"]
    formattedEarliestDate = formatDate(dateobjectEaliest)
    formattedLatestDate = formatDate(str(lastDate.strftime('%Y-%m-%d %H:%M:%S')))
    celebrityscore = getClosestsCelebrities(username, overallScore, engine)
    allcelebrities = getAllCelebrities(engine)
    danishuserscore = getDanishUsersScore(overallScore, engine),
    nationalAverages = getNationalScores(engine)
    scoreEvolutionData = scoreEvolution(tweetsDict)
    averagesRange = getLowestAndHighestAverages(scoreEvolutionData)

    data = {
        "userinfo" : userinfo,
        "overallscore" : overallScore,
        "tweets" : { "happiest" : getHappiestTweet(tweetsOnlyScores), "saddest" : getSaddestTweet(tweetsOnlyScores) },
        "alltweets" : tweetsDict,
        "topfivewords" : topWords,
        "wordsmatched" : wordsAmount,
        "highestweekscore": highest,
        "lowestweekscore": lowest,
        "weekscores" : week,
        "tweetstart" :  formattedEarliestDate,
        "tweetend" : formattedLatestDate,
        "tweetsamount" : len(tweetsDict),
        "celebrityscore" : celebrityscore,
        "allcelebrities" : allcelebrities,
        "danishuserscore" : danishuserscore,
        "nationalAverages" : nationalAverages,
        "monthlyaverages" : scoreEvolutionData,
        "averagesRange" : averagesRange
    }

    pattern = "['\[\]]"
    pattern = re.compile(pattern)
    top5happiest = pattern.sub('', str(topWords["top"]))
    top5saddest = pattern.sub('', str(topWords["bottom"]))


    print("Overall: " + str(overallScore))
    print("Happiest: " + str(getHappiestTweet(tweetsOnlyScores)["score"]))
    print("Saddest: " + str(getSaddestTweet(tweetsOnlyScores)["score"]))
    print("Top 5 happiest: " + str(top5happiest))
    print("Top 5 saddest: " + str(top5saddest))
    print("Tweets amount: " + str(len(tweetsDict)))
    print("Words matched: " + str(wordsAmount))
    print("Highest weekday day: " + str(highest["Day"]))
    print("Highest weekday score: " + str(highest["Score"]))
    print("Lowest weekday day: " + str(lowest["Day"]))
    print("Lowest weekday score: " + str(lowest["Score"]))


    toc2 = time.perf_counter()
    print(f"Done in {toc2 - tic:0.4f} seconds")

    return data

# Get all tweets and collect them in a dictionary
def getTweetsDictRaw(allTweets):
    tic = time.perf_counter()
    tweets = {}
    wordDict = {}
    count = 1
    for tweet in allTweets:
        score, word  = sentiment.getHapinessScore(tweet.full_text)
        if score != -1:
            dict = { count : {"id" : tweet.id, "score" : score, "created" : str(tweet.created_at) }}
            tweets.update(dict)
            wordDict.update(word)
            count += 1
    toc = time.perf_counter()
    debugPrint(f"getTweetsDict in {toc - tic:0.4f} seconds")       
    return tweets, wordDict

def getTweetsDict(allTweets):
    dict, words = getTweetsDictRaw(allTweets)
    df = pd.DataFrame.from_dict(dict, orient='index')    
    result = df.to_json(orient="records")
    parsed = json.loads(result)
    return parsed, words 

# Only get tweet id's and scores
def tweetsOnlyScore(scores):
    tic = time.perf_counter()
    
    scoresOnly = {}
    for score in scores:
        dict = {score["id"] : score["score"]}
        scoresOnly.update(dict)

    toc = time.perf_counter()
    debugPrint(f"tweetsOnlyScore in {toc - tic:0.4f} seconds")
    
    return scoresOnly

# Get profile info from user
def getProfileInfo(username):
    tic = time.perf_counter()

    api = c.setupTwitterAuth()

    try:
        user = api.get_user(username)
    except TweepError as e:
        return {"Error" : e}
        
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
    debugPrint(f"getProfileInfo in {toc - tic:0.4f} seconds")
    return userInfo

# Get the happiest tweet posted by the user. Returns the id and score of the tweet.
def getHappiestTweet(scores): 
    tic = time.perf_counter()
    
    if (len(list(scores.items())) < 1):
        return

    tweet = max(scores.items(), key=operator.itemgetter(1))[0]
    score = max(scores.items(), key=operator.itemgetter(1))[1]
    id = str(tweet)

    toc = time.perf_counter()
    debugPrint(f"getHappiestTweet in {toc - tic:0.4f} seconds")
     
    return {"id" : id, "score" : float("{:.2f}".format(score))}

# Get the unhappiest tweet posted by the user. Returns the id and score of the tweet.
def getSaddestTweet(scores):
    tic = time.perf_counter()

    if (len(list(scores.items())) < 1):
        return
    
    tweet = min(scores.items(), key=operator.itemgetter(1))[0]
    score = min(scores.items(), key=operator.itemgetter(1))[1]
    id = str(tweet)

    toc = time.perf_counter()
    debugPrint(f"getSaddestTweet in {toc - tic:0.4f} seconds")
    
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
    debugPrint(f"getOverallScore in {toc - tic:0.4f} seconds")

    if (count==0):
        return -1
    else:
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

    weekdayNames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    highestScore = max(withoutNan)
    highestWeekday = weekdayNames[withoutNanList.index(highestScore)]

    lowestScore = min(withoutNan)
    lowestWeekday = weekdayNames[withoutNanList.index(lowestScore)]

    toc = time.perf_counter()
    debugPrint(f"getWeekScores in {toc - tic:0.4f} seconds")

    return ({"Day" : highestWeekday, "Score" : highestScore},
            {"Day" : lowestWeekday, "Score" : lowestScore}, {
            0 : {"Day" : weekdayNames[0], "Score" : withoutNan[0]}, 
            1 : {"Day" : weekdayNames[1], "Score" : withoutNan[1]},
            2 : {"Day" : weekdayNames[2], "Score" : withoutNan[2]},
            3 : {"Day" : weekdayNames[3], "Score" : withoutNan[3]},
            4 : {"Day" : weekdayNames[4], "Score" : withoutNan[4]},
            5 : {"Day" : weekdayNames[5], "Score" : withoutNan[5]},
            6 : {"Day" : weekdayNames[6], "Score" : withoutNan[6]}
            })

# Get the closest three scores from a list of chosen celebrities on Twitter
def getClosestsCelebrities(username, overallScore, engine):
    tic = time.perf_counter()

    celebScores  = pd.read_sql("celebrity", con=engine)
    celebScores = celebScores.drop(celebScores[(celebScores['username'].str.lower() == username.lower())].index)

    df_sort = celebScores.iloc[(celebScores['score']-overallScore).abs().argsort()[:3]]
    df_sort_on_score = df_sort.sort_values(by=['score'])
    
    result = df_sort_on_score.to_json(orient="records")
    parsed = json.loads(result)

    toc = time.perf_counter()
    debugPrint(f"getClosestsCelebrities in {toc - tic:0.4f} seconds")
    engine.dispose()

    return parsed

# Get the closest three scores from a list of chosen celebrities on Twitter
def getAllCelebrities(engine):
    tic = time.perf_counter()
    celebScores  = pd.read_sql("celebrity", con=engine)
    
    df_sort_on_score = celebScores.sort_values(by=['score'], ascending=False)
    
    result = df_sort_on_score.to_json(orient="records")
    parsed = json.loads(result)

    toc = time.perf_counter()
    debugPrint(f"getAllCelebrities in {toc - tic:0.4f} seconds")
    engine.dispose()

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

def scoreEvolution(tweetsDict):
    tic = time.perf_counter()
    earliestTweet = tweetsDict[len(tweetsDict)-1]["created"]
    latestTweet = tweetsDict[0]["created"]

    earliestTweet = datetime.datetime.strptime(earliestTweet, '%Y-%m-%d %H:%M:%S')
    latestTweet = datetime.datetime.strptime(latestTweet, '%Y-%m-%d %H:%M:%S')

    num_months = (latestTweet.year - earliestTweet.year) * 12 + (latestTweet.month - earliestTweet.month)
    num_weeks = (abs(earliestTweet - latestTweet).days) // 7
    num_days = (latestTweet - earliestTweet).days
    dateArray = []

    Xmin = 100.0
    Xmax = 0.0
    tooltip = []
    lastDateCount = 0
    global lastDate

    if (num_months > 12): 
        dateArray = [0.0] * num_months
        tooltip = [""] * num_months
        currentMonth = latestTweet.month
        count = 0
        scoreSum = 0
        tweetNumber = 0
        diff = 1
        for tweet in tweetsDict:
            date = tweet["created"]
            dateObject = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            if count == 0:
                lastDate = dateObject
            if dateObject.month != currentMonth:
                diff = currentMonth - dateObject.month
                if diff < 1:
                    diff = diff + 12
                currentMonth = dateObject.month
                if tweetNumber != 0:
                    value = float("{:.2f}".format(scoreSum / tweetNumber))
                    dateArray[count] = value
                    if value != 0:
                        tooltip[count] = str(dateObject.month) + "/" + str(dateObject.year)
                        if lastDateCount == 0:
                            lastDate = dateObject
                            lastDateCount = 1
                        if value < Xmin:
                            Xmin = value
                        elif value > Xmax:
                            Xmax = value
                else:
                    value = float("{:.2f}".format(scoreSum))
                    dateArray[count] = value
                    if value != 0:
                        tooltip[count] = str(dateObject.month) + "/" + str(dateObject.year)
                        if lastDateCount == 0:
                            lastDate = dateObject
                            lastDateCount = 1
                        if value < Xmin:
                            Xmin = value
                        elif value > Xmax:
                            Xmax = value
                count = count + diff
                scoreSum = 0
                tweetNumber = 0
            else: 
                scoreSum = scoreSum + tweet["score"]
                tweetNumber = tweetNumber + 1
    elif (num_weeks > 12):
        dateArray = [0.0] * num_weeks
        tooltip = [""] * num_weeks
        currentWeek = latestTweet.isocalendar()[1]
        count = 0
        scoreSum = 0
        tweetNumber = 0
        diff = 1
        for tweet in tweetsDict:
            date = tweet["created"]
            dateObject = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            if count == 0:
                lastDate = dateObject
            if dateObject.isocalendar()[1] != currentWeek:
                diff = currentWeek - dateObject.isocalendar()[1]
                if diff < 1:
                    diff = diff + 51
                if count >= len(dateArray):
                    count = count - 1
                currentWeek = dateObject.isocalendar()[1]
                if tweetNumber != 0:
                    value = float("{:.2f}".format(scoreSum / tweetNumber))
                    dateArray[count] = value
                    if value != 0:
                        tooltip[count] = "Week " + str(dateObject.isocalendar()[1]) + " " + str(dateObject.year)
                        if lastDateCount == 0:
                            lastDate = dateObject
                            lastDateCount = 1
                        if value < Xmin:
                            Xmin = value
                        elif value > Xmax:
                            Xmax = value
                else:
                    value = float("{:.2f}".format(scoreSum))
                    dateArray[count] = value
                    if value != 0:
                        tooltip[count] = "Week " + str(dateObject.isocalendar()[1]) + " " + str(dateObject.year)
                        if lastDateCount == 0:
                            lastDate = dateObject
                            lastDateCount = 1
                        if value < Xmin:
                            Xmin = value
                        elif value > Xmax:
                            Xmax = value
                count = count + diff
                scoreSum = 0
                tweetNumber = 0
            else: 
                scoreSum = scoreSum + tweet["score"]
                tweetNumber = tweetNumber + 1
    else:
        dateArray = [0.0] * (num_days + 1)
        tooltip = [""] * (num_days + 1)
        currentDay = latestTweet.day
        count = 0
        scoreSum = 0
        tweetNumber = 0
        diff = 1
        for tweet in tweetsDict:
            date = tweet["created"]
            dateObject = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            if dateObject.day != currentDay:
                diff = currentDay - dateObject.day
                if diff < 1:
                    diff = diff + 30
                currentDay = dateObject.day
                if tweetNumber != 0:
                    value = float("{:.2f}".format(scoreSum / tweetNumber))
                    dateArray[count] = value
                    if value != 0:
                        tooltip[count] = str(dateObject.day) + "/" + str(dateObject.month) + "/" + str(dateObject.year)
                        if lastDateCount == 0:
                            lastDate = dateObject
                            lastDateCount = 1
                        if value < Xmin:
                            Xmin = value
                        elif value > Xmax:
                            Xmax = value
                else:
                    value = float("{:.2f}".format(scoreSum))
                    dateArray[count] = value
                    if value != 0:
                        tooltip[count] = str(dateObject.day) + "/" + str(dateObject.month) + "/" + str(dateObject.year)
                        if lastDateCount == 0:
                            lastDate = dateObject
                            lastDateCount = 1
                        if value < Xmin:
                            Xmin = value
                        elif value > Xmax:
                            Xmax = value
                count = count + diff
                scoreSum = 0
                tweetNumber = 0
            else: 
                scoreSum = scoreSum + tweet["score"]
                tweetNumber = tweetNumber + 1

    dateArray = list(filter((0.0).__ne__, reversed(dateArray)))
    newDateArray = [0.0] * len(dateArray)

    tooltip = list(filter(("").__ne__, reversed(tooltip)))

    count = 0
    for score in dateArray:
        Xnorm = (score - Xmin) / (Xmax - Xmin)
        dateArray[count] = Xnorm
        if count >= 4:
            movAvg = (Xnorm + dateArray[count-1] + dateArray[count-2] + dateArray[count-3] + dateArray[count-4]) / 5
            newDateArray[count] = [movAvg, count+1, tooltip[count]]
        elif count == 3:
            movAvg = (Xnorm + dateArray[count-1] + dateArray[count-2] + dateArray[count-3]) / 4
            newDateArray[count] = [movAvg, count+1, tooltip[count]]
        elif count == 2:
            movAvg = (Xnorm + dateArray[count-1] + dateArray[count-2]) / 3
            newDateArray[count] = [movAvg, count+1, tooltip[count]]
        elif count == 1:
            movAvg = (Xnorm + dateArray[count-1]) / 2
            newDateArray[count] = [movAvg, count+1, tooltip[count]]
        else:
            newDateArray[count] = [Xnorm, count+1, tooltip[count]]
        count = count + 1

    toc = time.perf_counter()
    debugPrint(f"scoreEvolution in {toc - tic:0.4f} seconds")

    return newDateArray

def getLowestAndHighestAverages(scoreEvolution):
    lowestScore = 1.0
    highestScore = 0.0
    for data in scoreEvolution:
        if data[0] < lowestScore:
            lowestScore = data[0]
        elif data[0] > highestScore:
            highestScore = data[0]
    
    res = [lowestScore, highestScore]
    return res

def getDanishUsersScore(overallScore, engine):
    tic = time.perf_counter()
    df = pd.read_sql("danish_users", con=engine)
    df_sort = df.sort_values(by=['score'])
    
    danishOverall = float("{:.2f}".format((int(df_sort["score"].mean()*100)/100.0)))
    amountOfUsers = len(df_sort.index)

    over = len(df_sort[(df_sort['score']>overallScore)])
    under = len(df_sort[(df_sort['score']>overallScore)])

    percent = int(over/len(df_sort)*100)

    toc = time.perf_counter()
    debugPrint(f"getDanishUsersScore in {toc - tic:0.4f} seconds")
    engine.dispose()
    return {"danishoverall" : danishOverall, "usersamount" : amountOfUsers, "usersless" : under, "percent" : percent}

def getUSAUsersScore(engine):
    tic = time.perf_counter()
    df = pd.read_sql("usa_users", con=engine)
    df_sort = df.sort_values(by=['score'])
    
    overall = float("{:.2f}".format((int(df_sort["score"].mean()*100)/100.0)))

    toc = time.perf_counter()
    debugPrint(f"getUSAUsersScore in {toc - tic:0.4f} seconds")
    engine.dispose()
    return {"overall" : overall, "countryCode" : "usa", "countryName" : "USA"}

def getUKUsersScore(engine):
    tic = time.perf_counter()
    df = pd.read_sql("uk_users", con=engine)
    df_sort = df.sort_values(by=['score'])
    
    overall = float("{:.2f}".format((int(df_sort["score"].mean()*100)/100.0)))

    toc = time.perf_counter()
    debugPrint(f"getUKUsersScore in {toc - tic:0.4f} seconds")
    engine.dispose()
    return {"overall" : overall, "countryCode" : "gb", "countryName" : "UK"}

def getSwedenUsersScore(engine):
    tic = time.perf_counter()
    df = pd.read_sql("sweden_users", con=engine)
    df_sort = df.sort_values(by=['score'])
    
    overall = float("{:.2f}".format((int(df_sort["score"].mean()*100)/100.0)))

    toc = time.perf_counter()
    debugPrint(f"getSwedenUsersScore in {toc - tic:0.4f} seconds")
    engine.dispose()
    return {"overall" : overall, "countryCode" : "swe", "countryName" : "Sweden"}

def getNorwayUsersScore(engine):
    tic = time.perf_counter()
    df = pd.read_sql("norway_users", con=engine)
    df_sort = df.sort_values(by=['score'])
    
    overall = float("{:.2f}".format((int(df_sort["score"].mean()*100)/100.0)))

    toc = time.perf_counter()
    debugPrint(f"getNorwayUsersScore in {toc - tic:0.4f} seconds")
    engine.dispose()
    return {"overall" : overall, "countryCode" : "nor", "countryName" : "Norway"}

def getGermanyUsersScore(engine):
    tic = time.perf_counter()
    df = pd.read_sql("germany_users", con=engine)
    df_sort = df.sort_values(by=['score'])
    
    overall = float("{:.2f}".format((int(df_sort["score"].mean()*100)/100.0)))
    
    toc = time.perf_counter()
    debugPrint(f"getGermanyUsersScore in {toc - tic:0.4f} seconds")
    engine.dispose()
    return {"overall" : overall, "countryCode" : "de", "countryName" : "Germany"}

def getNationalScores(engine):
    tic = time.perf_counter()
    scores = [getUSAUsersScore(engine), getUKUsersScore(engine), getSwedenUsersScore(engine), getNorwayUsersScore(engine), getGermanyUsersScore(engine)]

    sort = sorted(scores, key = lambda i: i['overall'])
    toc = time.perf_counter()
    debugPrint(f"getNationalScores in {toc - tic:0.4f} seconds")
    
    return sort

# Print debug messages
def debugPrint(text):
    if (debug):
        print(text)
    else:
        return

getData("MisterBens0n", 3200)
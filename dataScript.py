import methods as m
import configscript
import tweepy as tw
import pandas as pd
from sqlalchemy import create_engine, engine
import re
import numpy as np

engine = create_engine('postgresql://efkgjaxasehspw:7ebb68899129ff95e09c3000620892ac7804d150083b80a3a8fc632d1ab250cb@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/dfnb8s6k7aikmo')
   

# Random tweets from Denmark
def putDataDB():
    engine = create_engine('postgresql://efkgjaxasehspw:7ebb68899129ff95e09c3000620892ac7804d150083b80a3a8fc632d1ab250cb@ec2-54-216-185-51.eu-west-1.compute.amazonaws.com:5432/dfnb8s6k7aikmo')
    api = configscript.setupTwitterAuth()
    places = api.geo_search(query="Denmark", granularity="country")
    place_id = places[0].id
    tweets = tw.Cursor(api.search, q="place:%s" % place_id, tweet_mode='extended', lang='en').items()
    df = pd.DataFrame.from_dict(m.getTweetsDictRaw(tweets), orient='index')
    df.set_index('id', inplace=True)
    df.to_sql('tweets', con=engine, if_exists='append')

    engine.execute("DELETE FROM tweets T1 USING tweets T2 WHERE  T1.ctid  < T2.ctid AND  T1.id    = T2.id AND  T1.score = T2.score AND  T1.created = T2.created;")
    
    engine.dispose()
    #read  = pd.read_sql("tweets", con=engine) 

def celebrityScore(username):
    print(username)
    global engine
    api = configscript.setupTwitterAuth()
    allTweets = tw.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended", exclude_replies=False, include_rts=False, lang='en').items()
    listAllTweets = list(allTweets)

    if (len(listAllTweets) == 0):
        return

    tweetsDict = m.getTweetsDict(listAllTweets)

    score = m.getOverallScore(tweetsDict)
    
    if (score==-1):
        return

    user = api.get_user(username) 
    # Remove _normal from profile image URL
    profile_image_url = user.profile_image_url_https
    url = re.sub('_normal', '', profile_image_url)

    dict = {username : {"score" : score, "pic": url}} 

    df = pd.DataFrame.from_dict(dict, orient='index')
    df.index.name = 'username'
    df.to_sql('celebrity', con=engine, if_exists='append')

    engine.execute("DELETE FROM celebrity T1 USING celebrity T2 WHERE  T1.ctid  < T2.ctid AND  T1.username = T2.username;")

    engine.dispose()
    #read  = pd.read_sql("celebrity", con=engine)



def runceleb():
    celeb = ["elonmusk", "DonaldJTrumpJr", "BillGates", "JuddApatow", "Sethrogen", "BarackObama", "HamillHimself", "GretaThunberg", "tedcruz", "VancityReynolds", "RobertDowneyJr", "MarkRuffalo", "taylorswift13", "ladygaga", "rihanna", "azizansari", "ConanOBrien", "SteveMartinToGo", "rickygervais", "amyschumer", "Cristiano", "vElizabethOlsen", "shakira", "ddlovato", "chrisbrown", "EmmaWatson", "britneyspears", "selenagomez", "jtimberlake", "KimKardashian", "MariahCarey", "SHAQ", "lancearmstrong", "rainnwilson", "cher", "KimKardashian", "AlYankovic", "StephenAtHome", "ArianaGrande", "justinbieber", "NASA", "jimmyfallon", "KingJames", "MileyCyrus", "JLo", "Oprah", "BrunoMars", "NiallOfficial", "Drake", "KylieJenner", "KevinHart4real", "Harry_Styles", "wizkhalifa", "Louis_Tomlinson", "LilTunechi", "POTUS45", "Pink", "HillaryClinton", "aliciakeys", "JoeBiden", "ShawnMendes", "ActuallyNPH", "pitbull", "Eminem", "NICKIMINAJ", "StephenKing", "SachaBaronCohen", "rustyrockets", "stephenfry"]
    for c in celeb:
        celebrityScore(c)


def putDataForUser():
    global engine
    api = configscript.setupTwitterAuth()
    places = api.geo_search(query="Denmark", granularity="country")
    place_id = places[0].id
    tweets = tw.Cursor(api.search, q="place:%s" % place_id, tweet_mode='extended', lang='en').items()

    for tweet in tweets:
        username = tweet.user.screen_name
        allTweets = tw.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended", exclude_replies=False, include_rts=False, lang='en').items(10)
        listAllTweets = list(allTweets)
        if (len(listAllTweets) < 1):
            continue

        tweetsDict = m.getTweetsDict(listAllTweets)

        score = m.getOverallScore(tweetsDict)
        tweetsonlyscore = m.tweetsOnlyScore(tweetsDict)
        scoremax = m.getHappiestTweet(tweetsonlyscore)
        scoremin = m.getSaddestTweet(tweetsonlyscore)

        dict = {username : {"score" : score, "min" :  scoremin["score"], "max" : scoremax["score"]}} 
        df = pd.DataFrame.from_dict(dict, orient='index')
        df.index.name = 'username'
        df.to_sql('danish_users', con=engine, if_exists='append')

        engine.execute("DELETE FROM danish_users T1 USING danish_users T2 WHERE  T1.ctid  < T2.ctid AND  T1.username = T2.username;")

    engine.dispose()
        #read  = pd.read_sql("danish_users", con=engine)

def putDataForUserUSA():
    global engine
    api = configscript.setupTwitterAuth()
    places = api.geo_search(query="USA", granularity="country")
    place_id = places[0].id
    tweets = tw.Cursor(api.search, q="place:%s" % place_id, tweet_mode='extended', lang='en').items()

    for tweet in tweets:
        username = tweet.user.screen_name
        allTweets = tw.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended", exclude_replies=False, include_rts=False, lang='en').items(150)
        listAllTweets = list(allTweets)
        if (len(listAllTweets) < 1):
            continue
        tweetsDict = m.getTweetsDict(listAllTweets)

        score = m.getOverallScore(tweetsDict)
        tweetsonlyscore = m.tweetsOnlyScore(tweetsDict)
        scoremax = m.getHappiestTweet(tweetsonlyscore)
        scoremin = m.getSaddestTweet(tweetsonlyscore)

        dict = {username : {"score" : score, "min" :  scoremin["score"], "max" : scoremax["score"]}} 

        df = pd.DataFrame.from_dict(dict, orient='index')
        df.index.name = 'username'
        df.to_sql('usa_users', con=engine, if_exists='append')

        engine.execute("DELETE FROM usa_users T1 USING usa_users T2 WHERE  T1.ctid  < T2.ctid AND  T1.username = T2.username;")
        
    engine.dispose()
        #read  = pd.read_sql("usa_users", con=engine)


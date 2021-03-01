import methods as m
import config
import tweepy as tw
import pandas as pd
from sqlalchemy import create_engine
import re

def putDataDB():
    engine = create_engine('postgres://fptgchibpcgsug:82c819e919e1b13f7e80f667ac1ddbc0eb85747a59a3360ab77175992f88eb2d@ec2-52-209-134-160.eu-west-1.compute.amazonaws.com:5432/dermsjvi46fmof')
    api = config.setupTwitterAuth()
    places = api.geo_search(query="Denmark", granularity="country")
    place_id = places[0].id
    tweets = tw.Cursor(api.search, q="place:%s" % place_id, tweet_mode='extended', lang='en').items()
    df = pd.DataFrame.from_dict(m.getTweetsDict(tweets), orient='index')
    df.set_index('id', inplace=True)
    df.to_sql('tweets', con=engine, if_exists='append')

    engine.execute("DELETE FROM tweets T1 USING tweets T2 WHERE  T1.ctid  < T2.ctid AND  T1.id    = T2.id AND  T1.score = T2.score AND  T1.created = T2.created;")
  
    read  = pd.read_sql("tweets", con=engine) 



def celebrityScore(username):
    engine = create_engine('postgres://fptgchibpcgsug:82c819e919e1b13f7e80f667ac1ddbc0eb85747a59a3360ab77175992f88eb2d@ec2-52-209-134-160.eu-west-1.compute.amazonaws.com:5432/dermsjvi46fmof')
    api = config.setupTwitterAuth()
    
    allTweets = tw.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended", exclude_replies=False, include_rts=False, lang='en').items(30)
    listAllTweets = list(allTweets)
    tweetsDict = m.getTweetsDict(listAllTweets)

    score = m.getOverallScore(tweetsDict)
    
    user = api.get_user(username) 
    # Remove _normal from profile image URL
    profile_image_url = user.profile_image_url_https
    url = re.sub('_normal', '', profile_image_url)

    dict = {username : {"score" : score, "pic": url}} 

    df = pd.DataFrame.from_dict(dict, orient='index')
    df.index.name = 'username'
    df.to_sql('celebrity', con=engine, if_exists='append')

    engine.execute("DELETE FROM celebrity T1 USING celebrity T2 WHERE  T1.ctid  < T2.ctid AND  T1.username = T2.username;")

    read  = pd.read_sql("celebrity", con=engine)



def runceleb():
    celeb = ["elonmusk", "DonaldJTrumpJr", "BillGates", "JuddApatow", "Sethrogen", "BarackObama", "HamillHimself", "GretaThunberg", "tedcruz", "VancityReynolds", "RobertDowneyJr", "MarkRuffalo", "taylorswift13", "ladygaga", "britneyspears", "rihanna", "MariahCarey"]
    for c in celeb:
        celebrityScore(c)
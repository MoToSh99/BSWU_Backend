import methods as m
import config
import tweepy as tw
import pandas as pd
import os

# Appends up to 3000 of the newest tweets posted from Denmark to the data file
def getGeo():
    api = config.setupTwitterAuth()
    places = api.geo_search(query="Denmark", granularity="country")
    place_id = places[0].id
    tweets = tw.Cursor(api.search, q="place:%s" % place_id, tweet_mode='extended', lang='en').items(3000)
    if not os.path.isfile('data.csv'):
        df = pd.DataFrame.from_dict(m.getTweetsDict(tweets), orient='index')
        df.set_index('id', inplace=True)
        df.to_csv('data.csv')
    else: 
        dfOld = pd.read_csv("data.csv")
        dict = m.getTweetsDict(tweets)
        dfUpdate = pd.DataFrame.from_dict(dict, orient='index')
        dfNew = dfOld.append(dfUpdate, sort=True)
        dfNew.set_index('id', inplace=True)
        dfNewWithoutDup = dfNew.reset_index().drop_duplicates(subset='id', keep='last').set_index('id').sort_index()
        dfNewWithoutDup.to_csv("data.csv")

getGeo()
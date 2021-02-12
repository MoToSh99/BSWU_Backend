import methods as m
import config
import tweepy as tw
import pandas as pd

# Initializes the data file that is used for the country-wide tweet analysis
def getGeoInit():
    api = config.setupTwitterAuth()
    places = api.geo_search(query="Denmark", granularity="country")
    place_id = places[0].id
    tweets = tw.Cursor(api.search, q="place:%s" % place_id, tweet_mode='extended').items(100)
    df = pd.DataFrame.from_dict(m.getTweetsDict(tweets), orient='index')
    df.set_index('id', inplace=True)
    df.to_csv("data.csv")

# Appends up to 3000 of the newest tweets posted from Denmark to the data file
def getGeo():
    api = config.setupTwitterAuth()
    places = api.geo_search(query="Denmark", granularity="country")
    place_id = places[0].id
    tweets = tw.Cursor(api.search, q="place:%s" % place_id, tweet_mode='extended').items(3200)
    dfOld = pd.read_csv("data.csv")
    dfUpdate = pd.DataFrame.from_dict(m.getTweetsDict(tweets), orient='index')
    dfNew = dfOld.append(dfUpdate, sort=True)
    dfNew.set_index('id', inplace=True)
    dfNewWithoutDup = dfNew.reset_index().drop_duplicates(subset='id', keep='last').set_index('id').sort_index()
    dfNewWithoutDup.to_csv("data.csv")

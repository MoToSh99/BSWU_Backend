import methods as m
import config
import tweepy as tw
import pandas as pd
import os
from sqlalchemy import create_engine

# Appends up to 3000 of the newest tweets posted from Denmark to the DB



def putDataDB():
    engine = create_engine('postgres://fptgchibpcgsug:82c819e919e1b13f7e80f667ac1ddbc0eb85747a59a3360ab77175992f88eb2d@ec2-52-209-134-160.eu-west-1.compute.amazonaws.com:5432/dermsjvi46fmof')
    api = config.setupTwitterAuth()
    places = api.geo_search(query="Denmark", granularity="country")
    place_id = places[0].id
    tweets = tw.Cursor(api.search, q="place:%s" % place_id, tweet_mode='extended', lang='en').items(10)
    df = pd.DataFrame.from_dict(m.getTweetsDict(tweets), orient='index')
    df.reset_index().drop_duplicates(subset='id', keep='last').set_index('id').sort_index()
    df.to_sql('tweets', con=engine, if_exists='append')


putDataDB()
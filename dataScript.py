import methods as m
import config
import tweepy as tw


def getGeo():
    api = config.setupTwitterAuth()
    places = api.geo_search(query="USA", granularity="country")
    place_id = places[0].id
    tweets = tw.Cursor(api.search, q="place:%s" % place_id, tweet_mode='extended').items(100)

    return m.getTweetsDict(tweets)

print(getGeo())
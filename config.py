import tweepy as tw
from decouple import config

def setupTwitterAuth(): 
    # Keys for Twitter authentication
    consumer_key = config('TWITTER_CONSUMER_KEY')
    consumer_secret= config('TWITTER_COMSUMER_SECRET')
    access_token = config('TWITTER_ACCESS_TOKEN')
    access_token_secret = config('TWITTER_ACCESS_TOKEN_SECRET')

    # Authenticate user
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Use tweepy api
    return tw.API(auth, wait_on_rate_limit=True)
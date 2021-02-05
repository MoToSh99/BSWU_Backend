import tweepy as tw
import config

# Set up Twitter API
api = config.setupTwitterAuth()

# Get tweets from given user as text
def getTweets(username):
    # Weird twitter user for testing: STANN_co
    allTweets = tw.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended", exclude_replies=False, include_rts=False).items()
    tweetList = []
    for status in allTweets:
        tweetList.append(status.full_text)
    return tweetList
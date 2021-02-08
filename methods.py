import tweepy as tw
from tweepy.models import User
import config
import re
import sentiment

# Set up Twitter API
api = config.setupTwitterAuth()
username = ""
allTweets = ""



def setupUser(user):
    global username, allTweets
    username = user
    allTweets = tw.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended", exclude_replies=False, include_rts=False).items(10)
    return 0
    


# Get maximum latest tweets from user
def getTweets(username):
    # Weird twitter user for testing: STANN_co
    allTweets = tw.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended", exclude_replies=False, include_rts=False).items()
    tweetList = []
    for status in allTweets:
        tweetList.append(status.full_text)
    return tweetList

# Get profile info from user
def getProfileInfo(username):
    user = api.get_user(username) 

    # Remove _normal from profile image URL
    profile_image_url = user.profile_image_url_https
    url = re.sub('_normal', '', profile_image_url)
    print("The profile_image_url_https is : " + url) 

    userInfo = {
        "name" : user.name,
        "username" : user.screen_name,
        "location" : str(user.location),
        "profile_location" : str(user.profile_location),
        "geo_enabled" : str(user.geo_enabled),
        "followers_count" : str(user.followers_count),
        "friends_count" : str(user.friends_count),
        "verified" : str(user.verified),
        "profile_image_url" : url
    }

def getHappyTweet(username):
    hapinessScore = 0
    tweetID = ""
    for tweet in allTweets:
        newScore = sentiment.getHapinessScore(tweet.full_text)
        if newScore > hapinessScore:
           hapinessScore = newScore
           tweetID = tweet.id
    # TODO only ID
    html = '<blockquote class="twitter-tweet"><a href="https://twitter.com/x/status/{}"></a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'.format(tweetID)
        
    obj = {
        "id" : html
    }    
    return obj
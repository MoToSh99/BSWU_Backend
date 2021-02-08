import tweepy as tw
from tweepy.models import User
import config
import re
import sentiment
import operator

# Set up Twitter API

def setupUser(user):
    username = user
    allTweets = tw.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended", exclude_replies=False, include_rts=False).items(10)
    getProfileInfo(user())
    
    return 0


# Get maximum latest tweets from user
def getTweets(username):
    # Weird twitter user for testing: STANN_co
    setupUser(username)
    tweetList = []
    for status in allTweets:
        tweetList.append(status.full_text)
    return tweetList

# Get profile info from user
def getProfileInfo(username):
    api = config.setupTwitterAuth()
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



    return userInfo

def getHappyTweet(username):
    usr = setupUser(username)
    tweets = {}
    for tweet in allTweets:
        score = sentiment.getHapinessScore(tweet.full_text)
        if score != -1:
            dict = {tweet.id: score}
            tweets.update(dict)

       
    happy = max(tweets.items(), key=operator.itemgetter(1))[0]
    sad = min(tweets.items(), key=operator.itemgetter(1))[0]

    # TODO only ID
    html = '<blockquote class="twitter-tweet"><a href="https://twitter.com/x/status/{}"></a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'.format(happy)
     
    return sad

print(getHappyTweet("STANN_co"))

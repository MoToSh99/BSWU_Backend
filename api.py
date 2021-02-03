import os
import tweepy as tw
import pandas as pd
import sys
import json
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

# Set up Flask application
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Keys for Twitter authentication
consumer_key= '8XJfacAcQtqyyqkcK924dz63o'
consumer_secret= '71KcvzZhSOGWipDiTfcKXp9o1nF31X3HBWJJuSTZjuxTRaJW38'
access_token= '1347473963186868224-iW0Fzp9Zrjt04uipB4Uap34X3CfO0f'
access_token_secret= 'QwYU6arYs7N9uERLRbW94oJ2wvWrymsUjaCR2uvue0tHQ'

# Authenticate user
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Use tweepy api
api = tw.API(auth, wait_on_rate_limit=True)

#tweets = api.user_timeline('STANN_co', count=100, exclude_replies=True, include_rts=False)

""" i = 0
for status in tweets:
    print(status.text)
    print('*****************')
    i = i+1

print(i) """

"""
i = 1
for tweeties in tw.Cursor(api.user_timeline, screen_name='STANN_co', tweet_mode="extended", exclude_replies=False, include_rts=False).items():
    print(tweeties.full_text)
    print('************')
    i = i + 1
print(i)
"""
@app.route('/newesttweet')
@cross_origin()
def getMostRecentTweet():
    username = request.args.get('username')
    allTweets = tw.Cursor(api.user_timeline, count=1, screen_name='STANN_co', tweet_mode="extended", exclude_replies=False, include_rts=False).items()
    i = ""
    for status in allTweets:
        i = status.full_text
    return jsonify(i)

# Run application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5123)
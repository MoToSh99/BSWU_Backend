import os
import tweepy as tw
import sys
import json
import config
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import config

# Set up Flask application
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

api = config.setupTwitterAuth()

@app.route('/newesttweet')
@cross_origin()
def getMostRecentTweetsAPI():
    username = request.args.get('username')
    tweetList = getMostRecentTweets(username)
    return jsonify(tweetList)


def getMostRecentTweets(username):
    # STANN_co
    allTweets = tw.Cursor(api.user_timeline, screen_name=username, tweet_mode="extended", exclude_replies=False, include_rts=False).items()
    tweetList = []
    for status in allTweets:
        tweetList.append(status.full_text)
    return tweetList

# Run application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5123)
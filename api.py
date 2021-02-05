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
def getMostRecentTweets():
    username = request.args.get('username')
    allTweets = tw.Cursor(api.user_timeline, screen_name='STANN_co', tweet_mode="extended", exclude_replies=False, include_rts=False).items(10)
    tweetList = []
    for status in allTweets:
        tweetList.append(status.full_text)
    return jsonify(tweetList)

# Run application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5123)
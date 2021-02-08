from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import methods as m

# Set up Flask application
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Display the latest tweets
@app.route('/recenttweets')
@cross_origin()
def getMostRecentTweetsAPI():
    username = request.args.get('username')
    tweetList = m.getTweets(username)
    return jsonify(tweetList)

@app.route('/setupuser')
def setupUser():
    return jsonify(m.setupUser(request.args.get('username')))

@app.route('/profileinfo')
def getProfileInfo():
    return jsonify(m.getProfileInfo(request.args.get('username')))

@app.route('/gethappytweet')
def getHappyTweet():
    return jsonify(m.getHappyTweet(request.args.get('username')))

# Run application
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5123)
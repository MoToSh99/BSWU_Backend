from flask import Flask, request, jsonify
from time import sleep
import methods as m
import dataScript as d
from flask_cors import CORS, cross_origin
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(2)
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/userinfo')
def getUserInfo():
    return jsonify(m.getProfileInfo(request.args.get('username')))

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to HappyTweet 2.0 !</h1>"

@app.route('/gettwitterdata')
def getTwitterData():
    count = int(request.args.get('count'))
    username = request.args.get('username')
    return m.getData(username, count)

@app.route('/rating')
def rating():
    rating = int(request.args.get('rating'))
    username = str(request.args.get('username'))
    return d.sendRating(rating, username)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(host='0.0.0.0', threaded=True)
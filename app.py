from flask import Flask, request, jsonify
from time import sleep
import methods as m
from flask_cors import CORS, cross_origin
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(2)
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/getdata')
@cross_origin()
def getData():
    return jsonify(m.getData(request.args.get('username')))

@app.route('/userinfo')
@cross_origin()
def getUserInfo():
    return jsonify(m.getProfileInfo(request.args.get('username')))

# A welcome message to test our server
@app.route('/') 
@cross_origin()
def index():
    return "<h1>Welcome to HappyTweet !!</h1>"


@app.route('/gettwitterdata')
def getTwitterData():
    count = int(request.args.get('count'))
    username = request.args.get('username')
    if (username in m.listAllTweets):
        m.listAllTweets.pop(username)
    executor.submit(m.getTwitterData, username, count)
    return {"msg" : "Calling Twitter API in the background!"}

@app.route('/checkusername')
def checkData():
    username = request.args.get('username')
    if (username in m.listAllTweets):
        return {"Userdata" : True}
    else:
        return {"Userdata" : False}


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000, ssl_context='adhoc')
from flask import Flask, request, jsonify
from time import sleep
import methods as m
app = Flask(__name__)

@app.route('/getdata')
def getData():
    count = int(request.args.get('count'))
    if count == None:
        count = 3200
    return jsonify(m.getData(request.args.get('username'), count))

@app.route('/userinfo')
def getUserInfo():
    return jsonify(m.getProfileInfo(request.args.get('username')))

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to HappyTweet !!</h1>"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
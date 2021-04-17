from flask import Flask, request, jsonify
from time import sleep
import methods as m
from flask_cors import CORS, cross_origin
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(2)
app = Flask(__name__)
cors = CORS(app)


@app.route('/getdata')
def getData():
    count = int(request.args.get('count'))
    response = jsonify(m.getData(request.args.get('username'), count))
    return response

@app.route('/userinfo')
def getUserInfo():
    response = jsonify(m.getProfileInfo(request.args.get('username')))
    return response

# A welcome message to test our server
@app.route('/') 
@cross_origin()
def index():
    return "<h1>Welcome to HappyTweet !!</h1>"


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(host='0.0.0.0', threaded=True)
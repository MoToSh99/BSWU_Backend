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
    count = int(request.args.get('count'))
    if count == None:
        count = 3200
    return jsonify(m.getData(request.args.get('username'), count))

@app.route('/userinfo')
@cross_origin()
def getUserInfo():
    return jsonify(m.getProfileInfo(request.args.get('username')))

# A welcome message to test our server
@app.route('/')
@cross_origin()
def index():
    return "<h1>Welcome to HappyTweet !!</h1>"


@app.route('/jobs')
def run_jobs():
    executor.submit(some_long_task1)
    return 'Two jobs were launched in background!'


@app.route('/checkTwitter')
def checkData():
    if len(m.listAllTweets) != 0:
        return "True" 
    else:
        return "False"

def some_long_task1():
    print("Task #1 started!")
    sleep(10)
    m.listAllTweets = [1,2,4]
    print("Task #1 is done!")
    executor.submit(some_long_task2, 'hello', 123)


def some_long_task2(arg1, arg2):
    print("Task #2 started with args: %s %s!" % (arg1, arg2))
    sleep(5)
    print(m.listAllTweets)
    print("Task #2 is done!")


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
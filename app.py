from flask import Flask, request, jsonify
from time import sleep
import methods as m
from flask_cors import CORS, cross_origin
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

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
from time import sleep
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import methods as m
import dataScript as ds

# Set up Flask application
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/getdata')
def getData():
    return jsonify(m.getData(request.args.get('username')))


@app.route('/startgeo')
def startGeo():
    ds.getGeoLoop
    return "Starting geo loop"



# Run application
if __name__ == '__main__':
    app.run(host='localhost', port=5124)




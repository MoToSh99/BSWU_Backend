from time import sleep
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import methods as m

# Set up Flask application
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/getdata')
def getData():
    count = int(request.args.get('count'))
    if count == None:
        count = 3200
    return jsonify(m.getData(request.args.get('username'), count))


# Run application
if __name__ == '__main__':
    app.run(threaded=True, port=5000)




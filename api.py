from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import methods as m

# Set up Flask application
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/getdata')
def getData():
    return jsonify(m.getData(request.args.get('username')))

# Run application
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5124)
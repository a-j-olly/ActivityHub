from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/hello', methods=['GET'])
def hello_world():
    return jsonify({
        "message": "Hello World from ActivityHub API!",
        "status": "success"
    })

if __name__ == '__main__':
    app.run(debug=True)
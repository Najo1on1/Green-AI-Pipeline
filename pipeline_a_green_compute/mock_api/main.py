from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route('/intensity', methods=['GET'])
def get_carbon():
    # Simulate a grid that fluctuates
    return jsonify({"intensity": random.randint(50, 400)})

if __name__ == '__main__':
    # Run on all interfaces
    app.run(host='0.0.0.0', port=5000)
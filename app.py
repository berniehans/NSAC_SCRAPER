from flask import Flask, jsonify, send_from_directory
import subprocess
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/data')
def get_data():
    try:
        with open('history.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "history.json not found. Run the scraper first."}), 404

@app.route('/api/run-scraper')
def run_scraper():
    try:
        # We need to run the scraper with rye
        process = subprocess.Popen(["rye", "run", "python", "scraper.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # This is a simplified way to get the output. For real-time updates, a different approach (e.g., websockets) would be needed.
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            return jsonify({"message": "Scraper ran successfully.", "output": stdout})
        else:
            return jsonify({"message": "Scraper failed.", "error": stderr}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred.", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
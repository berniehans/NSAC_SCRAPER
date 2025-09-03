"""
This module contains the Flask web application for the NASA Space Apps Challenge Scraper.

It provides a web interface to view the scraped data, trigger the scraper, and export data to CSV.
"""
import csv
import io
import json
import subprocess

from flask import Flask, Response, jsonify, render_template

app = Flask(__name__, template_folder="../../templates", static_folder="../../static")


@app.route("/")
def index():
    """Renders the main dashboard page."""
    return render_template("index.html")


@app.route("/matrix")
def matrix():
    """Renders the historical matrix page."""
    return render_template("matrix.html")


@app.route("/api/data")
def get_data():
    """Returns the historical data from history.json."""
    try:
        with open("data/history.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "history.json not found. Run the scraper first."}), 404


@app.route("/api/run-scraper")
def run_scraper():
    """
    Runs the scraper as a subprocess.

    Returns:
        A JSON response with the scraper's output or an error message.
    """
    try:
        # We need to run the scraper with rye
        process = subprocess.Popen(
            ["rye", "run", "python", "src/nsac_scraper/scraper.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # This is a simplified way to get the output. For real-time updates, a different approach (e.g., websockets) would be needed.
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            return jsonify({"message": "Scraper ran successfully.", "output": stdout})
        else:
            return jsonify({"message": "Scraper failed.", "error": stderr}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred.", "error": str(e)}), 500


@app.route("/api/history-to-csv")
def history_to_csv():
    """
    Converts the history.json data to a CSV file and returns it as a download.
    """
    try:
        with open("data/history.json", "r") as f:
            history_data = json.load(f)

        if not history_data:
            return jsonify({"message": "No data in history.json to convert."}), 404

        # Collect all unique challenge names to use as CSV headers
        all_challenges = set()
        for entry in history_data:
            for challenge in entry.get("challenges", []):
                all_challenges.add(challenge.get("challenge"))
        sorted_challenges = sorted(list(all_challenges))

        # Prepare CSV header
        fieldnames = ["Timestamp"] + sorted_challenges

        # Generate CSV rows
        csv_rows = []
        for entry in history_data:
            row = {"Timestamp": entry.get("timestamp")}
            challenge_map = {
                c.get("challenge"): c.get("team_count")
                for c in entry.get("challenges", [])
            }
            for challenge_name in sorted_challenges:
                row[challenge_name] = challenge_map.get(challenge_name, 0)
            csv_rows.append(row)

        if not csv_rows:
            return (
                jsonify(
                    {"message": "No challenge data found in history.json to convert."}
                ),
                404,
            )

        # Create a CSV in memory
        si = io.StringIO()
        writer = csv.DictWriter(si, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(csv_rows)

        output = si.getvalue()

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=history.csv"},
        )

    except FileNotFoundError:
        return jsonify({"error": "history.json not found. Run the scraper first."}), 404
    except Exception as e:
        return (
            jsonify(
                {"message": "An error occurred during CSV conversion.", "error": str(e)}
            ),
            500,
        )


if __name__ == "__main__":
    app.run(debug=True)

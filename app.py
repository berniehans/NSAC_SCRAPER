import csv
import io
import json
import subprocess

from flask import Flask, Response, jsonify, send_from_directory

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/matrix")
def matrix():
    return send_from_directory(".", "matrix.html")


@app.route("/api/data")
def get_data():
    try:
        with open("history.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "history.json not found. Run the scraper first."}), 404


@app.route("/api/run-scraper")
def run_scraper():
    try:
        # We need to run the scraper with rye
        process = subprocess.Popen(
            ["rye", "run", "python", "scraper.py"],
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
    try:
        with open("history.json", "r") as f:
            history_data = json.load(f)

        if not history_data:
            return jsonify({"message": "No data in history.json to convert."}), 404

        # Prepare data for CSV
        csv_rows = []
        for entry in history_data:
            timestamp = entry.get("timestamp")
            for challenge in entry.get("challenges", []):
                csv_rows.append(
                    {
                        "timestamp": timestamp,
                        "challenge": challenge.get("challenge"),
                        "team_count": challenge.get("team_count"),
                    }
                )

        if not csv_rows:
            return (
                jsonify(
                    {"message": "No challenge data found in history.json to convert."}
                ),
                404,
            )

        # Create a CSV in memory
        si = io.StringIO()
        fieldnames = ["timestamp", "challenge", "team_count"]
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

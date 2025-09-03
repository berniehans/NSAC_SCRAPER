"""
This module contains the Flask web application for the NASA Space Apps Challenge Scraper.

It provides a web interface to view the scraped data, trigger the scraper, and export data to CSV.
"""

import asyncio  # Import asyncio
import csv
import io
import json
import threading  # Import threading

from flask import Flask, Response, jsonify, render_template

app = Flask(__name__, template_folder="../../templates", static_folder="../../static")

scraper_running = False


@app.route("/api/scraper-status")
def get_scraper_status():
    global scraper_running
    return jsonify({"status": "running" if scraper_running else "idle"})


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
        with open("data/history.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "history.json not found. Run the scraper first."}), 404


@app.route("/api/run-scraper")
def run_scraper():
    """
    Triggers the scraper to run in a separate thread.
    """

    def run_scraper_async_in_thread():
        global scraper_running
        scraper_running = True
        try:
            # Import scraper_main here to avoid circular imports and ensure it's loaded in the new thread
            from src.nsac_scraper.scraper import main as scraper_main

            asyncio.run(scraper_main())
        finally:
            scraper_running = False

    try:
        thread = threading.Thread(target=run_scraper_async_in_thread)
        thread.daemon = (
            True  # Allow main program to exit even if thread is still running
        )
        thread.start()
        return (
            jsonify(
                {
                    "message": "Scraper started successfully in the background.",
                    "status": "running",
                }
            ),
            202,
        )
    except Exception as e:
        return jsonify({"message": "Failed to start scraper.", "error": str(e)}), 500


@app.route("/api/history-to-csv")
def history_to_csv():
    """
    Converts the history.json data to a CSV file and returns it as a download.
    """
    try:
        with open("data/history.json", "r", encoding="utf-8") as f:
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
                jsonify({"message": "No data in history.json to convert."}),
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
    app.run(debug=True)  # nosec

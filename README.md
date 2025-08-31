# NASA Space Apps Challenge Scraper

This project is a web scraper that collects the number of teams participating in the NASA Space Apps Challenge. It scrapes the data from the official website and provides a web interface to view the current and historical data.

## Features

*   **Data Scraping**: Scrapes team counts for various challenges from the NASA Space Apps Challenge website.
*   **Data Storage**: Stores scraped data, including timestamps, in `teams.json`.
*   **Web Interface**: A Flask-based web application to:
    *   Display current team counts.
    *   Manually trigger data updates.
    *   Export historical data to CSV.
    *   View a historical matrix of team counts.
    *   Visualize the evolution of team counts for each challenge over time using a line chart.

## How to use

1.  **Install dependencies:**

    This project uses [Rye](https://rye-up.com/) to manage dependencies. If you don't have Rye installed, please follow the instructions on the official website.

    ```bash
    rye sync
    ```

2.  **Run the web application:**

    ```bash
    rye run flask --app app.py run
    ```
    Access the web interface at `http://127.0.0.1:5000/`.

3.  **Run the scraper (via web interface):**
    On the main dashboard, click the "Update Data" button to run the scraper and fetch the latest team counts.

4.  **Code Review and Formatting:**

    To run code formatting and linting checks:
    ```bash
    rye run review
    ```

## Data

The `teams.json` file contains a list of challenges with the number of teams for each challenge, along with a timestamp of when the data was scraped.

Example:
```json
{
    "timestamp": "2025-08-31T16:56:36.825275+00:00",
    "challenges": [
        {
            "challenge": "Animation Celebration Of Terra Data",
            "team_count": 87
        },
        {
            "challenge": "A World Away Hunting For Exoplanets With Ai",
            "team_count": 373
        },
        ...
    ]
}
```
# NASA Space Apps Challenge Scraper

This project is a web scraper that collects the number of teams participating in the NASA Space Apps Challenge. It scrapes the data from the official website and provides a web interface to view the current and historical data.

## Features

*   **Data Scraping**: Scrapes team counts for various challenges from the NASA Space Apps Challenge website.
*   **Data Storage**: Stores scraped data, including timestamps, in `data/history.json` and the latest scrape in `data/teams.json`.
*   **Web Interface**: A Flask-based web application to:
    *   Display current team counts.
    *   Manually trigger data updates.
    *   Export historical data to CSV.
    *   View a historical matrix of team counts.
    *   Visualize the evolution of team counts for each challenge over time using a line chart.

## Project Structure

```
.
├── data
│   ├── history.json      # History of scraped data (gitignored)
│   └── teams.json        # Latest scraped data (gitignored)
├── src
│   └── nsac_scraper
│       ├── __init__.py
│       ├── app.py          # Flask application
│       └── scraper.py      # Scraper logic
├── static
│   └── js
│       ├── index.js
│       └── matrix.js
├── templates
│   ├── index.html
│   └── matrix.html
├── .gitignore
├── config.json             # Configuration for the scraper
├── pyproject.toml          # Project configuration for rye
├── README.md
└── ...
```

## How to use

1.  **Install dependencies:**

    This project uses [Rye](https://rye-up.com/) to manage dependencies. If you don't have Rye installed, please follow the instructions on the official website.

    ```bash
    rye sync
    ```

2.  **Run the web application:**

    ```bash
    rye run flask --app src/nsac_scraper/app run
    ```
    Access the web interface at `http://127.0.0.1:5000/`.

3.  **Run the scraper (via web interface):**
    On the main dashboard, click the "Update Data" button to run the scraper and fetch the latest team counts.

4.  **Code Review and Formatting:**

    To run code formatting and linting checks:
    ```bash
    rye run review
    ```

## API Endpoints

The application provides the following API endpoints:

*   `GET /`: Main dashboard.
*   `GET /matrix`: View a historical matrix of team counts.
*   `GET /api/data`: Get the latest scraped data in JSON format.
*   `GET /api/run-scraper`: Trigger the scraper to run.
*   `GET /api/history-to-csv`: Export the historical data to a CSV file.

## Data

The `data/teams.json` and `data/history.json` files contain the scraped data. These files are generated at runtime and are not tracked by git (see `.gitignore`).

Example of `teams.json`:
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
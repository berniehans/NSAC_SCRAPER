# Web Scraper Project

## Objective

Create a web scraper using Playwright to extract the number of teams from a list of challenge URLs from the NASA Space Apps Challenge website.

## Requirements

1.  **Extract Data:**
    *   Scrape the number of teams for each challenge from the provided list of URLs.
    *   The XPath of the element to scrape is: `/html/body/main/section/div/div[3]/div/div/div/div[3]/div/p`
    *   The text to extract is similar to: "Currently returning 373 teams"
    *   From this text, only the number (e.g., `373`) should be kept.
    *   The challenge title should be extracted from the URL slug.

2.  **Storage:**
    *   The extracted data should be saved in a JSON file named `teams.json`.
    *   The JSON file should contain a timestamp and a list of challenges with their team counts.
    *   The scraper should be designed to be run on demand.

## URLs

The scraper uses a predefined list of challenge URLs.

## Web Interface

A Flask-based web application (`app.py`) has been implemented to provide a user interface for the scraper data.

### `index.html`

*   **Purpose**: Main dashboard to display current team counts, trigger scraper runs, and export data.
*   **Changes**:
    *   Removed the "Historical Matrix" navigation link from the top navigation bar.
    *   Removed the "Historical Matrix" section (heading and table) from the main content area.
    *   Removed the JavaScript code responsible for rendering the matrix table within this page.

### `matrix.html`

*   **Purpose**: Dedicated page to display the historical matrix of team counts and their evolution over time.
*   **Changes**:
    *   Added a navigation bar at the top to allow easy switching between the "Main Dashboard" and "Historical Matrix" pages.
    *   Integrated the Chart.js library for data visualization.
    *   Added a `<canvas>` element to render a line chart.
    *   Implemented JavaScript logic to:
        *   Fetch historical data.
        *   Process the data to create datasets for each challenge.
        *   Render a responsive line chart showing the evolution of team counts for each challenge across different timestamps. Random colors are generated for each line.

## Project Configuration (`pyproject.toml`)

*   **Development Dependencies**:
    *   Added `black`, `isort`, and `ruff` to the `dev-dependencies` list under `[tool.rye]`.
*   **Rye Scripts**:
    *   The `review` script under `[tool.rye.scripts]` has been updated. It now includes the `--fix` option for `ruff check .`, allowing automatic fixing of linting issues when the script is run.

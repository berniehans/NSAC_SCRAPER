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
    *   The extracted data is saved in a JSON format.
    *   `data/history.json` stores the history of all scrapes.
    *   `data/teams.json` stores the latest scrape.
    *   The scraper is designed to be run on demand.

3.  **Configuration:**
    *   The scraper configuration (URLs and XPath) is stored in `config.json`.

## Project Structure

The project is organized as follows:

```
.
├── data
│   ├── history.json
│   └── teams.json
├── src
│   └── nsac_scraper
│       ├── __init__.py
│       ├── app.py
│       └── scraper.py
├── static
│   └── js
│       ├── index.js
│       └── matrix.js
├── templates
│   ├── index.html
│   └── matrix.html
├── .gitignore
├── config.json
├── pyproject.toml
└── README.md
```

## Web Interface

A Flask-based web application (`src/nsac_scraper/app.py`) provides a user interface for the scraper data.

### `templates/index.html` & `templates/matrix.html`

*   The HTML files for the web interface.

### `static/js/`

*   The JavaScript files for the web interface, `index.js` and `matrix.js`, are located here.

## Project Configuration (`pyproject.toml`)

*   **Development Dependencies**:
    *   Added `black`, `isort`, and `ruff` to the `dev-dependencies` list under `[tool.rye]`.
*   **Rye Scripts**:
    *   The `review` script under `[tool.rye.scripts]` has been updated. It now includes the `--fix` option for `ruff check .`, allowing automatic fixing of linting issues when the script is run.
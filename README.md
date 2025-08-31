# NASA Space Apps Challenge Scraper

This project is a web scraper that collects the number of teams participating in the NASA Space Apps Challenge. It scrapes the data from the official website and saves it to a JSON file.

## How to use

1.  **Install dependencies:**

    This project uses [Rye](https://rye-up.com/) to manage dependencies. If you don't have Rye installed, please follow the instructions on the official website.

    ```bash
    rye sync
    ```

2.  **Run the scraper:**

    ```bash
    rye run python scraper.py
    ```

    This will create a `teams.json` file with the scraped data.
    
    ```bash
    rye run flask --app app.py run
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
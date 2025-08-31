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
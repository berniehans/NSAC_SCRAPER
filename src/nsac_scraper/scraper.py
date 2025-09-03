"""
This script scrapes team count data from the NASA Space Apps Challenge website.

It reads a list of challenge URLs and an XPath from a config.json file,
scrapes the data, and saves it to history.json and teams.json.
"""
import json
import re
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright


def scrape_challenge_data(urls, xpath):
    """
    Scrapes the team count and challenge title from a list of challenge URLs.

    Args:
        urls (list): A list of challenge URLs.
        xpath (str): The XPath of the element containing the team count text.

    Returns:
        list: A list of dictionaries, where each dictionary contains the challenge title and team count.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        results = []
        for i, url in enumerate(urls):
            try:
                page.goto(url, wait_until="networkidle")

                # Scrape team count
                team_count_element = page.locator(f"xpath={xpath}")
                team_count_text = team_count_element.inner_text(timeout=5000)
                team_count_match = re.search(r"\d+", team_count_text)
                team_count = int(team_count_match.group(0)) if team_count_match else 0

                # Get title from URL
                slug = url.split("/")[-2]
                title = slug.replace("-", " ").title()

                results.append({"challenge": title, "team_count": team_count})
                print(
                    f"({i+1}/{len(urls)}) Successfully scraped {team_count} teams for '{title}'"
                )

            except Exception as e:
                print(f"Could not scrape data for {url}. Error: {e}")

        browser.close()
        return results


def save_to_history(data, filename):
    """
    Saves data to a history JSON file.

    Args:
        data (dict): The data to save.
        filename (str): The name of the JSON file.
    """
    history = []
    try:
        with open(filename, "r") as f:
            history = json.load(f)
    except FileNotFoundError:
        pass  # File doesn't exist yet

    history.append(data)

    with open(filename, "w") as f:
        json.dump(history, f, indent=4)


if __name__ == "__main__":
    # Load configuration from config.json
    with open("config.json", "r") as f:
        config = json.load(f)

    CHALLENGE_URLS = config["CHALLENGE_URLS"]
    XPATH = config["XPATH"]

    # Scrape the data
    results = scrape_challenge_data(CHALLENGE_URLS, XPATH)

    # Prepare the output data with a timestamp
    output_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "challenges": results,
    }

    # Save the data to history.json and teams.json
    save_to_history(output_data, "data/history.json")
    with open("data/teams.json", "w") as f:
        json.dump(output_data, f, indent=4)

    print("Scraping complete. Data saved to history.json and teams.json")

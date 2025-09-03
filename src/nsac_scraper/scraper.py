"""
This script scrapes team count data from the NASA Space Apps Challenge website.

It reads a list of challenge URLs and an XPath from a config.json file,
scrapes the data, and saves it to history.json and teams.json.
"""

import json
import re
import asyncio
from datetime import datetime, timezone

from playwright.async_api import async_playwright
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


# Define a retry decorator for network operations
@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(Exception),
)
async def goto_with_retry(page, url):
    """Navigates to a URL with retry logic."""
    await page.goto(url, wait_until="networkidle")


async def scrape_single_challenge(url, xpath, browser):
    """
    Scrapes the team count and challenge title from a single challenge URL.
    Uses an existing browser instance.
    """
    page = await browser.new_page()
    try:
        # Simulate realistic web request headers
        await page.set_extra_http_headers(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

        await goto_with_retry(page, url)

        # Scrape team count
        team_count_element = page.locator(f"xpath={xpath}")
        team_count_text = await team_count_element.inner_text(timeout=5000)
        team_count_match = re.search(r"\d+", team_count_text)
        team_count = int(team_count_match.group(0)) if team_count_match else 0

        # Get title from URL
        slug = url.split("/")[-2]
        title = slug.replace("-", " ").title()

        print(f"Successfully scraped {team_count} teams for '{title}'")
        return {"challenge": title, "team_count": team_count}

    except Exception as e:
        print(f"Could not scrape data for {url}. Error: {e}")
        return {"challenge": url, "team_count": 0, "error": str(e)}  # Return error info
    finally:
        await page.close()


async def scrape_challenge_data(urls, xpath):
    """
    Scrapes the team count and challenge title from a list of challenge URLs concurrently.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        tasks = [scrape_single_challenge(url, xpath, browser) for url in urls]
        results = await asyncio.gather(*tasks)
        await browser.close()
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
        with open(filename, "r", encoding="utf-8") as f:
            history = json.load(f)
    except FileNotFoundError:
        pass  # File doesn't exist yet

    history.append(data)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)


async def main():
    # Load configuration from config.json
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    CHALLENGE_URLS = config["CHALLENGE_URLS"]
    XPATH = config["XPATH"]

    # Scrape the data
    results = await scrape_challenge_data(CHALLENGE_URLS, XPATH)

    # Prepare the output data with a timestamp
    output_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "challenges": results,
    }

    # Save the data to history.json and teams.json
    save_to_history(output_data, "data/history.json")
    with open("data/teams.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)

    print("Scraping complete. Data saved to history.json and teams.json")


if __name__ == "__main__":
    asyncio.run(main())

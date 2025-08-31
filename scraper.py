
import json
import re
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone

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
                team_count_match = re.search(r'\d+', team_count_text)
                team_count = int(team_count_match.group(0)) if team_count_match else 0
                
                # Get title from URL
                slug = url.split('/')[-2]
                title = slug.replace('-', ' ').title()

                results.append({
                    "challenge": title,
                    "team_count": team_count
                })
                print(f"({i+1}/{len(urls)}) Successfully scraped {team_count} teams for '{title}'")

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
        with open(filename, 'r') as f:
            history = json.load(f)
    except FileNotFoundError:
        pass # File doesn't exist yet

    history.append(data)

    with open(filename, 'w') as f:
        json.dump(history, f, indent=4)

if __name__ == "__main__":
    CHALLENGE_URLS = [
        "https://www.spaceappschallenge.org/2025/challenges/animation-celebration-of-terra-data/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/a-world-away-hunting-for-exoplanets-with-ai/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/bloomwatch-an-earth-observation-application-for-global-flowering-phenology/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/build-a-space-biology-knowledge-engine/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/commercializing-low-earth-orbit-leo/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/create-your-own-challenge/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/data-pathways-to-healthy-cities-and-human-settlements/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/deep-dive-immersive-data-stories-from-ocean-to-sky/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/embiggen-your-eyes/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/from-earthdata-to-action-cloud-computing-with-earth-observation-data-for-predicting-cleaner-safer-skies/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/international-space-station-25th-anniversary-apps/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/meteor-madness/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/nasa-farm-navigators-using-nasa-data-exploration-in-agriculture/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/sharks-from-space/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/spacetrash-hack-revolutionizing-recycling-on-mars/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/stellar-stories-space-weather-through-the-eyes-of-earthlings/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/through-the-radar-looking-glass-revealing-earth-processes-with-sar/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/will-it-rain-on-my-parade/?tab=teams",
        "https://www.spaceappschallenge.org/2025/challenges/your-home-in-space-the-habitat-layout-creator/?tab=teams"
    ]
    XPATH = "/html/body/main/section/div/div[3]/div/div/div/div[3]/div/p"
    
    results = scrape_challenge_data(CHALLENGE_URLS, XPATH)

    output_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "challenges": results
    }

    save_to_history(output_data, "history.json")
    # also save the latest scrape to teams.json for the simple dashboard
    with open("teams.json", "w") as f:
        json.dump(output_data, f, indent=4)

    print("Scraping complete. Data saved to history.json and teams.json")

# scraper.py
import requests
from bs4 import BeautifulSoup
import json
import logging

logger = logging.getLogger(__name__)

def fetch_airdrops_and_save():
    url = "https://airdrops.io/free-airdrops/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        airdrops = []

        # Find airdrop cards — adjust selectors if website layout changes
        airdrop_cards = soup.select(".airdrops-list .airdrop")  # class names may change!

        for card in airdrop_cards[:6]:  # take first 6 airdrops (free + premium)
            title_tag = card.select_one(".airdrop__title")
            link_tag = card.select_one("a")
            description_tag = card.select_one(".airdrop__description")

            if not title_tag or not link_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = link_tag['href']
            description = description_tag.get_text(strip=True) if description_tag else "No description."

            airdrops.append({
                "title": title,
                "link": link,
                "description": description
            })

        with open("airdrops.json", "w", encoding="utf-8") as f:
            json.dump(airdrops, f, indent=4, ensure_ascii=False)

        logger.info("Successfully saved latest airdrops to airdrops.json")

    except Exception as e:
        logger.error(f"Error fetching or parsing airdrops: {e}")

# For manual testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetch_airdrops_and_save()

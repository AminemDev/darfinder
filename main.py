import os
import requests
from bs4 import BeautifulSoup
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Search criteria
SEARCH_KEYWORDS = ["cité ghazela", "حي الغزالة", "ghazela"]
MAX_PRICE = 980000
MIN_ROOMS = 3

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        logging.info("Telegram message sent.")
    else:
        logging.error(f"Failed to send Telegram message: {response.text}")

def fetch_tayara():
    url = "https://www.tayara.tn/ads/l/Ariana/Ghazela/k/villa/?maxPrice=980000&page=1"
    logging.info(f"Fetching listings from: {url}")
    try:
        res = requests.get(url)
        res.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to fetch listings: {e}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("a.css-1c8trrd")
    logging.info(f"Found {len(items)} listings.")

    results = []

    for item in items:
        title_tag = item.select_one("h2")
        if not title_tag:
            continue

        title = title_tag.text.strip().lower()
        link = "https://www.tayara.tn" + item.get("href", "")
        price_tag = item.select_one("span[data-testid='ad-price']")
        price_text = price_tag.text.strip().replace("DT", "").replace(",", "").replace(" ", "") if price_tag else "0"
        price = int("".join(filter(str.isdigit, price_text))) if price_text else 0

        logging.info(f"Title: {title} | Price: {price} | Link: {link}")

        if any(keyword in title for keyword in SEARCH_KEYWORDS) and price <= MAX_PRICE:
            if any(f"s+{n}" in title for n in range(MIN_ROOMS, 7)):
                message = f"<b>{title.title()}</b>\n{price} TND\n{link}"
                results.append(message)
                logging.info("Matched and added to results.")

    return results

def main():
    logging.info("Starting Tayara scraper.")
    listings = fetch_tayara()
    if listings:
        logging.info(f"Sending {len(listings)} matching listing(s).")
        for listing in listings:
            send_telegram_message(listing)
    else:
        logging.info("No listings matched the filter.")
        send_telegram_message("No new listings found in Cité Ghazela today.")

if __name__ == "__main__":
    main()

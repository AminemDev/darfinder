import os
import requests
from bs4 import BeautifulSoup
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Constants
TAYARA_URL = "https://www.tayara.tn/ads/l/Ariana/Ghazela/k/villa/?maxPrice=980000&page=1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

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
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            logging.info("✅ Telegram message sent.")
        else:
            logging.error(f"❌ Telegram error {response.status_code}: {response.text}")
    except requests.RequestException as e:
        logging.error(f"❌ Telegram request failed: {e}")

def fetch_tayara():
    logging.info(f"🌐 Fetching listings from: {TAYARA_URL}")
    try:
        res = requests.get(TAYARA_URL, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except Exception as e:
        logging.error(f"❌ Failed to fetch listings: {e}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("a.css-1c8trrd")
    logging.info(f"🔍 Found {len(items)} listing(s).")

    results = []

    for item in items:
        title_tag = item.select_one("h2")
        if not title_tag:
            logging.warning("⚠️ Skipped listing with no title.")
            continue

        title = title_tag.text.strip().lower()
        href = item.get("href")
        if not href:
            logging.warning("⚠️ Skipped listing with no href.")
            continue

        link = "https://www.tayara.tn" + href
        price_tag = item.select_one("span[data-testid='ad-price']")
        price_text = price_tag.text.strip().replace("DT", "").replace(",", "").replace(" ", "") if price_tag else "0"
        price = int("".join(filter(str.isdigit, price_text))) if price_text else 0

        logging.info(f"📄 Title: {title} | 💰 Price: {price} | 🔗 Link: {link}")

        # Apply filters
        if any(keyword in title for keyword in SEARCH_KEYWORDS) and price <= MAX_PRICE:
            if any(f"s+{n}" in title for n in range(MIN_ROOMS, 7)):
                message = f"<b>{title.title()}</b>\n{price} TND\n{link}"
                results.append(message)
                logging.info("✅ Matched and added to results.")

    return results

def main():
    logging.info("🚀 Starting Tayara scraper.")
    listings = fetch_tayara()
    if listings:
        logging.info(f"📦 Sending {len(listings)} matching listing(s).")
        for listing in listings:
            send_telegram_message(listing)
    else:
        logging.info("🛑 No listings matched the filter.")
        send_telegram_message("No new listings found in Cité Ghazela today.")

if __name__ == "__main__":
    main()

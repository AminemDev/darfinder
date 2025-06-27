import os
import requests
from bs4 import BeautifulSoup
import logging

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Env variables ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- Filters ---
SEARCH_KEYWORDS = ["cité ghazela", "حي الغزالة", "ghazela"]
MAX_PRICE = 980000
MIN_ROOMS = 3

# --- Telegram function ---
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(url, data=data)
        if res.status_code == 200:
            logging.info("✅ Telegram message sent.")
        else:
            logging.error(f"❌ Telegram failed: {res.text}")
    except Exception as e:
        logging.error(f"❌ Telegram exception: {e}")

# --- Tayara scraper ---
def fetch_tayara():
    url = "https://www.tayara.tn/ads/l/Ariana/Ghazela/k/villa/?maxPrice=980000&page=1"
    logging.info(f"Tayara → Fetching: {url}")
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
    except Exception as e:
        logging.error(f"Tayara fetch failed: {e}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("a.css-1c8trrd")
    logging.info(f"🔍 Tayara found {len(items)} listing(s)")

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

        logging.info(f"Tayara listing: {title} | {price}TND | {link}")

        if any(k in title for k in SEARCH_KEYWORDS) and price <= MAX_PRICE:
            if any(f"s+{n}" in title for n in range(MIN_ROOMS, 7)):
                message = f"<b>{title.title()}</b>\n{price} TND\n{link}"
                results.append(message)
                logging.info("✅ Tayara → Matched and added to results")

    return results

# --- Almindhar scraper ---
def fetch_almindhar():
    url = "https://al-mindhar.com/search-results/?status%5B%5D=for-sale&states%5B%5D=ariana&location%5B%5D=&type%5B%5D=Villa&bedrooms=&bathrooms=&min-price=0&max-price=1029987&min-area=0&max-area=10000"
    logging.info(f"Almindhar → Fetching: {url}")
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
    except Exception as e:
        logging.error(f"Almindhar fetch failed: {e}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("div.property-item")
    logging.info(f"🔍 Almindhar found {len(items)} listing(s)")

    results = []
    for item in items:
        title_tag = item.select_one("h5 a")
        title = title_tag.text.strip().lower() if title_tag else ""
        link = title_tag["href"] if title_tag else ""
        price_tag = item.select_one(".property-price")
        price_text = price_tag.text.strip().replace("DT", "").replace(",", "").replace(" ", "") if price_tag else "0"
        price = int("".join(filter(str.isdigit, price_text))) if price_text else 0

        logging.info(f"Almindhar listing: {title} | {price}TND | {link}")

        if any(k in title for k in SEARCH_KEYWORDS) and price <= MAX_PRICE:
            message = f"<b>{title.title()}</b>\n{price} TND\n{link}"
            results.append(message)
            logging.info("✅ Almindhar → Matched and added to results")

    return results

# --- Main ---
def main():
    logging.info("📦 Starting DarFinder Bot")
    listings = []

    listings += fetch_tayara()
    listings += fetch_almindhar()

    if listings:
        logging.info(f"📬 Sending {len(listings)} listing(s)")
        for listing in listings:
            send_telegram_message(listing)
    else:
        logging.info("📭 No new listings matched.")
        send_telegram_message("No new listings found in Cité Ghazela today.")

if __name__ == "__main__":
    main()

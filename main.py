import os
import requests
from bs4 import BeautifulSoup
import logging

# === Configuration ===
SEARCH_KEYWORDS = ["cité ghazela", "حي الغزالة", "ghazela"]
MAX_PRICE = 980000
MIN_ROOMS = 3

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === Telegram Setup ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DEBUG_MODE = os.getenv("DEBUG_TELEGRAM") == "1"

def send_telegram_message(text, is_debug=False):
    if is_debug and not DEBUG_MODE:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        logging.info("📢 Telegram message sent.")
    else:
        logging.error(f"❌ Failed to send Telegram message: {response.text}")

def fetch_tayara():
    url = "https://www.tayara.tn/ads/l/Ariana/Ghazela/k/villa/?maxPrice=980000&page=1"
    logging.info(f"🌍 Fetching listings from: {url}")
    try:
        res = requests.get(url)
        res.raise_for_status()
    except Exception as e:
        logging.error(f"❌ Failed to fetch listings: {e}")
        send_telegram_message(f"❌ Failed to fetch listings: {e}", is_debug=True)
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    anchors = soup.find_all("a", href=True)
    listings = [a for a in anchors if "/item/" in a["href"] and a.find("h2", class_="card-title")]

    logging.info(f"🔍 Found {len(listings)} listing(s)")
    send_telegram_message(f"🔍 Found {len(listings)} listing(s)", is_debug=True)

    results = []

    for item in listings:
        title_tag = item.find("h2", class_="card-title")
        price_tag = item.find("data", class_="font-arabic")
        if not title_tag or not price_tag:
            continue

        title = title_tag.text.strip().lower()
        price_text = price_tag.text.strip().replace("DT", "").replace(",", "").replace(" ", "")
        price = int("".join(filter(str.isdigit, price_text))) if price_text else 0
        link = "https://www.tayara.tn" + item["href"]

        logging.info(f"📝 Title: {title} | 💰 Price: {price} | 🔗 {link}")

        if any(keyword in title for keyword in SEARCH_KEYWORDS) and price <= MAX_PRICE:
            if any(f"s+{n}" in title for n in range(MIN_ROOMS, 7)) or "immeuble" in title or "villa" in title:
                message = f"<b>{title.title()}</b>\n{price} TND\n{link}"
                results.append(message)
                logging.info("✅ Matched and added to results.")
            else:
                logging.info("ℹ️ Skipped: doesn't match room count.")

    return results

def main():
    logging.info("🚀 Starting Tayara scraper.")
    listings = fetch_tayara()
    if listings:
        logging.info(f"📨 Sending {len(listings)} matching listing(s).")
        for listing in listings:
            send_telegram_message(listing)
    else:
        logging.info("❓ No listings matched the filter.")
        send_telegram_message("❓ No new listings found in Cité Ghazela today.")

if __name__ == "__main__":
    main()

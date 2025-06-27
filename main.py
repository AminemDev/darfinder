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
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    resp = requests.post(url, data=data)
    if resp.status_code == 200:
        logging.info("✅ Telegram message sent.")
    else:
        logging.error(f"❌ Telegram error: {resp.text}")

# -------- Tayara Fetcher (existing) --------
def fetch_tayara():
    url = "https://www.tayara.tn/ads/l/Ariana/Ghazela/k/villa/?maxPrice=980000&page=1"
    logging.info(f"Tayara → Fetching: {url}")
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        logging.error(f"Tayara fetch failed: {e}")
        return []
    soup = BeautifulSoup(res.text, "html.parser")
    anchors = soup.find_all("a", href=True)
    items = [a for a in anchors if "/item/" in a["href"] and a.find("h2", class_="card-title")]
    logging.info(f"Tayara → Found {len(items)} listings")
    send_telegram_message(f"Tayara → Found {len(items)} listings", is_debug=True)
    results = []
    for item in items:
        title = item.find("h2", class_="card-title").text.strip().lower()
        price = int(''.join(filter(str.isdigit, item.find("data", class_="font-arabic").text))) \
                if item.find("data", class_="font-arabic") else 0
        link = "https://www.tayara.tn" + item["href"]
        logging.info(f"Tayara listing: {title} | {price}TND | {link}")
        if any(k in title for k in SEARCH_KEYWORDS) and price <= MAX_PRICE:
            if any(f"s+{n}" in title for n in range(MIN_ROOMS, 7)) or "villa" in title or "immeuble" in title:
                results.append(f"<b>{title.title()}</b>\n{price} TND\n{link}")
                logging.info("Tayara → Matched")
    return results

# -------- Mubawab Fetcher (new) --------
def fetch_mubawab():
    url = "https://www.mubawab.tn/sd/raoued/cit%C3%A9-el-ghazela/villas-et-maisons-de-luxe-a-vendre:prmx:1000000:emr:3"
    logging.info(f"Mubawab → Fetching: {url}")
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        logging.error(f"Mubawab fetch failed: {e}")
        return []
    soup = BeautifulSoup(res.text, "html.parser")
    cards = soup.find_all("article")
    logging.info(f"Mubawab → Found {len(cards)} cards")
    send_telegram_message(f"Mubawab → Found {len(cards)} listings", is_debug=True)
    results = []
    for c in cards:
        title_tag = c.find("h2")
        price_tag = c.find("div", class_="price")
        if not title_tag or not price_tag:
            continue
        title = title_tag.text.strip().lower()
        price = int(''.join(filter(str.isdigit, price_tag.text)))
        link = "https://www.mubawab.tn" + c.find("a", href=True)["href"]
        logging.info(f"Mubawab listing: {title} | {price}TND | {link}")
        if any(k in title for k in SEARCH_KEYWORDS) and price <= MAX_PRICE:
            rooms = any(f"{n} chambres" in c.text.lower() for n in range(MIN_ROOMS, 10))
            if rooms or "villa" in title or "maison" in title:
                results.append(f"<b>{title.title()}</b>\n{price} TND\n{link}")
                logging.info("Mubawab → Matched")
    return results

# -------- Main --------
def main():
    logging.info("🚀 Starting scraping process")
    results = fetch_tayara() + fetch_mubawab()
    if results:
        logging.info(f"📬 Sending {len(results)} listing(s)")
        for msg in results:
            send_telegram_message(msg)
    else:
        logging.info("❌ No listings matched filters")
        send_telegram_message("No new listings found in Cité Ghazela today.")

if __name__ == "__main__":
    main()

import os
import json
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, db

# Load Firebase config JSON from environment variable
firebase_config = json.loads(os.environ['FIREBASE_CONFIG_JSON'])

# Initialize Firebase app
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://dar-finder-default-rtdb.firebaseio.com'  # replace with your actual databaseURL
})

# Telegram details from environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Your search criteria
SEARCH_KEYWORDS = ["cité ghazela", "حي الغزالة"]
MAX_PRICE = 980000
MIN_ROOMS = 3

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

def has_been_seen(link):
    ref = db.reference("seen_links")
    seen_links = ref.get() or {}
    return link in seen_links

def mark_as_seen(link):
    ref = db.reference("seen_links")
    ref.update({link: True})

def fetch_tayara():
    url = "https://www.tayara.tn/ads/ar/search/real-estate/ariana/for-sale/apartments"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("a.css-1c8trrd")
    print(f"Found {len(items)} listings on Tayara")  # Debug info
    results = []

    for item in items:
        title_tag = item.select_one("h2")
        if not title_tag:
            print("Skipped an item with no title")
            continue
        title = title_tag.text.strip().lower()
        link = "https://www.tayara.tn" + item["href"]

        price_tag = item.select_one("span[data-testid='ad-price']")
        price_text = price_tag.text.strip().replace("DT", "").replace(",", "").replace(" ", "") if price_tag else "0"
        price = int("".join(filter(str.isdigit, price_text))) if price_text else 0

        print(f"Checking listing: '{title}', Price: {price}, Link: {link}")  # Debug

        if any(k in title for k in SEARCH_KEYWORDS) and price <= MAX_PRICE:
            if any(f"s+{n}" in title for n in range(MIN_ROOMS, 10)):
                if not has_been_seen(link):
                    print(f"New matching listing found: {link}")  # Debug
                    results.append(f"<b>{title.title()}</b>\n{price} TND\n{link}")
                    mark_as_seen(link)
                else:
                    print("Already seen this listing.")
            else:
                print("Does not match room count requirement.")
        else:
            print("Does not match keywords or price.")

    return results

def main():
    found = fetch_tayara()
    if found:
        for f in found:
            send_telegram_message(f)
    else:
        send_telegram_message("No new listings found in Cité Ghazela today.")

if __name__ == "__main__":
    main()

import os
import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SEARCH_KEYWORDS = ["cité ghazela", "حي الغزالة"]
MAX_PRICE = 980000

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

def fetch_tayara():
    url = "https://www.tayara.tn/ads/l/Ariana/Ghazela/k/villa/?maxPrice=980000&page=1"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("a")
    
    print(f"🔍 Found {len(items)} <a> tags on Tayara page")
    results = []

    scanned = 0
    for item in items:
        title = item.text.strip().lower()
        link = item.get("href")
        if not link or not title:
            continue
        scanned += 1
        if any(keyword in title for keyword in SEARCH_KEYWORDS):
            full_link = "https://www.tayara.tn" + link if link.startswith("/ads") else link
            results.append(f"<b>{title.title()}</b>\n{full_link}")

    print(f"✅ Scanned {scanned} valid ads, matched {len(results)} results")
    return results

@app.route('/')
def home():
    return "🏠 DarFinder is running."

@app.route('/trigger')
def trigger():
    print("🚀 Triggered bot run!")
    results = fetch_tayara()
    if results:
        for r in results:
            send_telegram_message(r)
        print(f"📬 Sent {len(results)} messages to Telegram.")
    else:
        send_telegram_message("No new listings found.")
        print("📭 No listings found. Sent fallback message.")
    return "Done"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

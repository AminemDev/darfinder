import os
import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SCRAPER_API_KEY = "9617853d9765799343a222e8f5d78960"

SEARCH_KEYWORDS = ["cité ghazela", "حي الغزالة", "ghazela", "غزالة"]
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
    url = "https://www.tayara.tn/ads/l/Ariana/Ghazela/k/villa/?maxPrice=980000"
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
    res = requests.get(proxy_url)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []
    items = soup.find_all("a")
    print(f"🔍 Found {len(items)} <a> tags on Tayara page")

    scanned = 0
    for item in items:
        title = item.get("title") or (item.find("h2").text.strip() if item.find("h2") else None)
        link = item.get("href")
        if not title or not link:
            continue

        scanned += 1
        title_lower = title.lower()
        if any(k in title_lower for k in SEARCH_KEYWORDS) and (
            "s+3" in title_lower or "s+4" in title_lower or "s+5" in title_lower or "villa" in title_lower
        ):
            results.append(f"<b>{title}</b>\nhttps://www.tayara.tn{link}")

    print(f"✅ Scanned {scanned} valid ads, matched {len(results)} results")
    return results, scanned

def main():
    found, scanned = fetch_tayara()
    if found:
        for f in found:
            send_telegram_message(f)
        send_telegram_message(f"📦 Checked {scanned} ads, found {len(found)} new listings in Cité Ghazela.")
    else:
        send_telegram_message(f"📦 Checked {scanned} ads — No new listings found in Cité Ghazela today.")

if __name__ == "__main__":
    main()

from flask import Flask

app = Flask(__name__)

@app.route('/')
def run_bot():
    main()
    return "✅ Bot ran successfully", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

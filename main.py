import os
import time
import requests
from bs4 import BeautifulSoup

# Config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")  # Add this in Render too!
SEARCH_KEYWORDS = ["cité ghazela", "حي الغزالة", "ghazela", "غزالة"]
MAX_PRICE = 980000

# Send Telegram message
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

# Scrape Tayara
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
            full_link = "https://www.tayara.tn" + link if link.startswith("/") else link
            results.append(f"<b>{title}</b>\n{full_link}")

    print(f"✅ Scanned {scanned} ads, matched {len(results)} results")
    return results, scanned

# Main loop
def run_forever(delay_minutes=60):
    while True:
        print("⏳ Checking listings...")
        try:
            found, scanned = fetch_tayara()
            if found:
                for f in found:
                    send_telegram_message(f)
                send_telegram_message(f"📦 Checked {scanned} ads, found {len(found)} new listings in Cité Ghazela.")
            else:
                send_telegram_message(f"📦 Checked {scanned} ads — No new listings found in Cité Ghazela.")
        except Exception as e:
            error_msg = f"❌ Error during check: {str(e)}"
            print(error_msg)
            send_telegram_message(error_msg)

        print(f"⏰ Sleeping for {delay_minutes} minutes...\n")
        time.sleep(delay_minutes * 60)

if __name__ == "__main__":
    delay = int(os.getenv("CHECK_DELAY", 60))  # Default 60 mins
    run_forever(delay)

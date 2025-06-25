import os
import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SCRAPER_API_KEY = "9617853d9765799343a222e8f5d78960"

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

def fetch_tayara():
    url = "https://www.tayara.tn/ads/c/Immobilier/Appartements/l/Ariana/Ghazela/"
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
    res = requests.get(proxy_url)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []
    items = soup.find_all("a")
    
    for item in items:
        # Try to get the title from 'title' attribute or <h2> tag
        title = item.get("title") or (item.find("h2").text.strip() if item.find("h2") else None)
        link = item.get("href")
        if not title or not link:
            continue

        title_lower = title.lower()
        if any(k in title_lower for k in SEARCH_KEYWORDS) and ("s+3" in title_lower or "s+4" in title_lower or "s+5" in title_lower):
            results.append(f"<b>{title}</b>\nhttps://www.tayara.tn{link}")
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

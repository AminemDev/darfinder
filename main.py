import os
import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SCRAPER_API_KEY = "9617853d9765799343a222e8f5d78960"

SEARCH_KEYWORDS = ["cité ghazela", "حي الغزالة"]
MAX_PRICE = 980000
MIN_ROOMS = 3
SEEN_FILE = "seen.txt"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

def load_seen_links():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_seen_link(link):
    with open(SEEN_FILE, "a") as f:
        f.write(link + "\n")

def fetch_tayara():
    url = "https://www.tayara.tn/ads/c/Immobilier/Appartements/l/Ariana/Ghazela/"
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
    res = requests.get(proxy_url)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []
    seen_links = load_seen_links()
    items = soup.find_all("a")
    
    for item in items:
        title = item.get("title") or (item.find("h2").text.strip() if item.find("h2") else None)
        link = item.get("href")
        if not title or not link:
            continue

        full_link = "https://www.tayara.tn" + link
        title_lower = title.lower()
        if (
            any(k in title_lower for k in SEARCH_KEYWORDS)
            and ("s+3" in title_lower or "s+4" in title_lower or "s+5" in title_lower)
            and full_link not in seen_links
        ):
            results.append(f"<b>{title}</b>\n{full_link}")
            save_seen_link(full_link)
    return results

def main():
    found = fetch_tayara()
    if found:
        for f in found:
            send_telegram_message(f)
    else:
        print("No new listings found.")

if __name__ == "__main__":
    main()

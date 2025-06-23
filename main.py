
import os
import requests
from bs4 import BeautifulSoup
import time

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
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
    url = "https://www.tayara.tn/ads/ar/search/real-estate/ariana/for-sale/apartments"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("a.css-1c8trrd")
    results = []
    for item in items:
        title = item.select_one("h2").text.strip().lower()
        link = "https://www.tayara.tn" + item["href"]
        price_tag = item.select_one("span[data-testid='ad-price']")
        price = price_tag.text.strip().replace("DT", "").replace(",", "").replace(" ", "") if price_tag else "0"
        price = int("".join(filter(str.isdigit, price))) if price else 0

        if any(k in title for k in SEARCH_KEYWORDS) and price <= MAX_PRICE:
            if "s+3" in title or "s+4" in title or "s+5" in title:
            results.append(f"<b>{title.title()}</b>\\n{price} TND\\n{link}")
{price} TND
{link}")
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

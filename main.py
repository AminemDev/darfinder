import os
import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SEARCH_KEYWORDS = ["cité ghazela", "حي الغزالة"]
MAX_PRICE = 980000

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    })

def fetch_tayara():
    url = "https://www.tayara.tn/ads/k/appartement%20à%20vendre%20ariana"
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    items = soup.select("a")  # Filter by keyword inside
    results = []
    for item in items:
        text = item.get_text().strip().lower()
        href = item.get("href", "")
        if "s+3" in text and any(k in text for k in SEARCH_KEYWORDS):
            # attempt to find price
            price_match = item.parent.find(text=True)  # fallback
            price = int("".join(filter(str.isdigit, price_match))) if price_match else 0
            if price <= MAX_PRICE:
                link = "https://www.tayara.tn" + href
                results.append(f"<b>{text.title()}</b>\n{price} TND\n{link}")
    return results

def fetch_mubawab():
    url = "https://www.mubawab.tn/fr/sd/ariana-ville/ariana/appartements-a-vendre"
    soup = BeautifulSoup(requests.get(url, headers={"User-Agent":"Mozilla/5.0"}).text, "html.parser")
    cards = soup.find_all("div", {"data-box-id": True})  # Generic listing container
    results = []
    for card in cards:
        text = card.get_text(separator=" ").strip().lower()
        if "s+3" in text and any(k in text for k in SEARCH_KEYWORDS):
            link_tag = card.select_one("a")
            price_tag = card.select_one("span")
            if link_tag and price_tag:
                price = int("".join(filter(str.isdigit, price_tag.text)))
                if price <= MAX_PRICE:
                    link = "https://www.mubawab.tn" + link_tag["href"]
                    results.append(f"<b>{text.title()}</b>\n{price} TND\n{link}")
    return results

def main():
    ads = fetch_tayara() + fetch_mubawab()
    if ads:
        for ad in ads:
            send_telegram_message(ad)
    else:
        send_telegram_message("No new listings found in Cité Ghazela today.")

if __name__ == "__main__":
    main()

import os
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KEYWORDS = ["s+3", "s+4", "s+5"]
LOCATION = "cité ghazela"
MAX_PRICE = 980000

def send(msg):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    })

def fetch_tayara():
    url = "https://www.tayara.tn/ads/c/Immobilier/Appartements/l/Ariana/Ghazela/"
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    cards = soup.select("a")
    print("TAYARA LISTINGS FOUND:")
    for card in cards:
        print(card.get("title", ""), card.get("href", ""))

def fetch_mubawab():
    url = "https://www.mubawab.tn/fr/cd/raoued/cit%C3%A9-el-ghazela/immobilier-a-vendre"
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    cards = soup.select("div[data-box-id]")
    results = []
    for c in cards:
        text = c.get_text(" ", strip=True).lower()
        if LOCATION in text and any(k in text for k in KEYWORDS):
            price_tag = c.select_one("div div:contains('TND')")
            price = int("".join(filter(str.isdigit, price_tag.text))) if price_tag else 0
            if price <= MAX_PRICE:
                link_tag = c.select_one("a")
                link = "https://www.mubawab.tn" + link_tag["href"]
                title = text[:50]  # brief title
                results.append(f"<b>{title.title()}</b>\n{price} TND\n{link}")
    return results

def main():
    ads = fetch_tayara() + fetch_mubawab()
    if ads:
        for ad in ads: send(ad)
    else:
        send("No new listings found in Cité Ghazela today.")

if __name__ == "__main__":
    main()

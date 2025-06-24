import requests
from bs4 import BeautifulSoup

def fetch_tayara_debug():
    url = "https://www.tayara.tn/ads/c/Immobilier/Appartements/l/Ariana/Ghazela/"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select("a")
        print("---- Tayara Results ----")
        for item in items:
            title = item.get("title")
            href = item.get("href")
            if title and href:
                print(title, "->", "https://www.tayara.tn" + href)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    fetch_tayara_debug()

import os
import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            logging.info("✅ Telegram message sent.")
        else:
            logging.error(f"❌ Telegram error: {response.status_code}, {response.text}")
    except Exception as e:
        logging.error(f"❌ Telegram exception: {e}")

def main():
    logging.info("📤 Sending Hello message to Telegram...")
    send_telegram_message("Hello from GitHub Actions 👋")

if __name__ == "__main__":
    main()

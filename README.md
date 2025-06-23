
# DarFinder Bot

A simple real estate monitoring bot that checks Tayara.tn for listings in Cité Ghazela, Ariana (Tunisia), filters by price and number of rooms, and sends alerts to Telegram.

## Filters:
- Price <= 980,000 TND
- At least S+3 (3 bedrooms)
- Location must include "Cité Ghazela" or "حي الغزالة"

## Hosting
- Hosted for free using [Render.com](https://render.com)
- Scheduled to run every 3 hours (can be changed)

## Setup Instructions

1. Create a Telegram Bot using @BotFather.
2. Get your Telegram `chat_id` from https://api.telegram.org/bot<your_token>/getUpdates
3. Upload these files to a GitHub repo.
4. Connect the repo to Render.
5. Add two environment variables:
   - TELEGRAM_TOKEN
   - TELEGRAM_CHAT_ID
6. Deploy as a cron job.

Enjoy your automated home-finder! 🏡

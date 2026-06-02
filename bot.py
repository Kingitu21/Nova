import time
import requests
import xml.etree.ElementTree as ET
from textblob import TextBlob
from datetime import datetime
import os
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = '5487451507'
GOLD_THRESHOLD = 2000
PROXY = {'https': 'http://proxy.server:3128'}

# ... keep all your get_gold_price, get_gold_news, send_telegram functions ...

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 GOLG SNIPER BOT is online!\nI’ll alert you when Gold > $2000 or big news hits.")

def alert_loop():
    print("Bot running... Telegram alerts: ACTIVE ✅")
    send_telegram("🤖 Gold Bot is LIVE!\nProxy fix applied. I'll alert you 24/7")
    counter = 0
    while True:
        try:
            price = get_gold_price()
            if price and price > GOLD_THRESHOLD:
                msg = f"🚨 GOLD ALERT!\nPrice: ${price:.2f}\nAbove ${GOLD_THRESHOLD}"
                send_telegram(msg)
            
            counter += 1
            if counter % 3 == 0:
                news_alerts = get_gold_news()
                for alert in news_alerts:
                    send_telegram(alert)
            
            time.sleep(600)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

# Run alert loop in background
threading.Thread(target=alert_loop, daemon=True).start()

# Run Telegram bot for replies
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
print("Reply bot started...")
app.run_polling()

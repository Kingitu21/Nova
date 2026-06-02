import time
import requests
import xml.etree.ElementTree as ET
from textblob import TextBlob
import os
import threading
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = '5487451507'
GOLD_THRESHOLD = 2000

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 GOLG SNIPER BOT online!\nCommands:\n/price - Current gold price\nJust say Hi!")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get("https://api.metals.live/v1/spot", timeout=10)
        price = float(r.json()[0]['gold'])
        await update.message.reply_text(f"💰 Current Gold: ${price:.2f}/oz")
    except Exception as e:
        await update.message.reply_text(f"Price check failed: {e}")

async def chatback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    blob = TextBlob(user_text)
    sentiment = blob.sentiment.polarity
    
    if sentiment > 0.3:
        reply = "Bullish vibes detected! 🚀 Gold moon soon?"
    elif sentiment < -0.3:
        reply = "Bearish mood... 📉 Stay strong, we HODL gold!"
    else:
        reply = "Yo! GOLG SNIPER here 😎 Gold alerts are ON!"
    
    await update.message.reply_text(reply)

def get_gold_news():
    try:
        r = requests.get("https://news.google.com/rss/search?q=gold+price&hl=en-US", timeout=10)
        root = ET.fromstring(r.content)
        alerts = []
        for item in root.findall('.//item')[:3]:
            title = item.find('title').text
            link = item.find('link').text
            sentiment = TextBlob(title).sentiment.polarity
            if abs(sentiment) > 0.3:
                mood = "BULLISH 🚀" if sentiment > 0 else "BEARISH 📉"
                alerts.append(f"{mood}\n{title}\n{link}")
        return alerts
    except:
        return []

def send_telegram(message):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'},
            timeout=10
        )
    except Exception as e:
        print(f"Telegram error: {e}")

def alert_loop():
    print("Bot running... Telegram alerts: ACTIVE ✅")
    send_telegram("🤖 Gold Bot is LIVE!\nNo proxy. I'll alert you 24/7 if gold > $2000")
    counter = 0
    while True:
        try:
            price = float(requests.get("https://api.metals.live/v1/spot", timeout=10).json()[0]['gold'])
            if price > GOLD_THRESHOLD:
                send_telegram(f"🚨 GOLD ALERT!\nPrice: ${price:.2f}/oz\nAbove ${GOLD_THRESHOLD}!")
            counter += 1
            if counter % 3 == 0:
                for alert in get_gold_news():
                    send_telegram(alert)
            time.sleep(600)
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(60)

# Start alerts in background thread
threading.Thread(target=alert_loop, daemon=True).start()

# Build app - v20.8 style, no Updater
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", price))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatback))

print("Chat bot started...")
app.run_polling(allowed_updates=Update.ALL_TYPES)

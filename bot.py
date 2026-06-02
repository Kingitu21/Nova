import time
import requests
import xml.etree.ElementTree as ET
from textblob import TextBlob
from datetime import datetime
import os
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = '5487451507'
GOLD_THRESHOLD = 2000
PROXY = PROXY = None  # Render has direct internet, no proxy needed

def get_gold_price():
    try:
        url = "https://api.metals.live/v1/spot"
        r = requests.get(url, proxies=PROXY, timeout=10)
        data = r.json()
        return float(data[0]['gold'])
    except:
        return None

def get_gold_news():
    try:
        url = "https://news.google.com/rss/search?q=gold+price&hl=en-US&gl=US&ceid=US:en"
        r = requests.get(url, proxies=PROXY, timeout=10)
        root = ET.fromstring(r.content)

        alerts = []
        for item in root.findall('.//item')[:3]:
            title = item.find('title').text
            link = item.find('link').text
            sentiment = TextBlob(title).sentiment.polarity

            if sentiment > 0.3 or sentiment < -0.3:
                mood = "BULLISH 🚀" if sentiment > 0 else "BEARISH 📉"
                alerts.append(f"{mood}\n{title}\n{link}")
        return alerts
    except:
        return []

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=data, proxies=PROXY, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

# ===== CHAT HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 GOLG SNIPER BOT is online!\n\n"
        "I do 2 things:\n"
        "1. Alert you 24/7 if Gold > $2000\n"
        "2. Chat with you anytime 💬\n\n"
        "Try: /price to check gold now"
    )

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_gold_price()
    if price:
        await update.message.reply_text(f"💰 Current Gold: ${price:.2f}/oz")
    else:
        await update.message.reply_text("Can't fetch price right now 😅")

async def chatback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "hello" in text or "hi" in text:
        await update.message.reply_text("Yo! GOLG SNIPER here 😎 Watching gold for you!")
    else:
        await update.message.reply_text(f"You said: {update.message.text}\nType /price to check gold")

# ===== ALERT LOOP =====
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

# Run Telegram bot for chat
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", price))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatback))
print("Chat bot started...")
app.run_polling()

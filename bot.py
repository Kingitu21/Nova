import time
import requests
import xml.etree.ElementTree as ET
from textblob import TextBlob
import os
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = '5487451507'
GOLD_THRESHOLD = 2000

# NO PROXY for Render
PROXY = None

def get_gold_price():
    try:
        url = "https://api.metals.live/v1/spot"
        r = requests.get(url, timeout=10) # removed proxies=PROXY
        return float(r.json()[0]['gold'])
    except:
        return None

def get_gold_news():
    try:
        url = "https://news.google.com/rss/search?q=gold+price&hl=en-US&gl=US&ceid=US:en"
        r = requests.get(url, timeout=10) # removed proxies=PROXY
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
        requests.post(url, data=data, timeout=10) # removed proxies=PROXY
    except Exception as e:
        print(f"Telegram error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 GOLG SNIPER BOT online!\nTry: /price")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_gold_price()
    await update.message.reply_text(f"💰 Gold: ${price:.2f}/oz" if price else "Price unavailable")

async def chatback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yo! GOLG SNIPER here 😎 Gold alerts are ON!")

def alert_loop():
    print("Bot running... Telegram alerts: ACTIVE ✅")
    send_telegram("🤖 Gold Bot is LIVE!\nProxy fix applied. I'll alert you 24/7")
    counter = 0
    while True:
        try:
            price = get_gold_price()
            if price and price > GOLD_THRESHOLD:
                send_telegram(f"🚨 GOLD ALERT!\nPrice: ${price:.2f}")
            counter += 1
            if counter % 3 == 0:
                for alert in get_gold_news():
                    send_telegram(alert)
            time.sleep(600)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

threading.Thread(target=alert_loop, daemon=True).start()

# THIS LINE FIXES THE PROXY ERROR FOR THE BOT
app = ApplicationBuilder().token(TELEGRAM_TOKEN).request_kwargs({"proxy_url": None}).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", price))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatback))
print("Chat bot started...")
app.run_polling()

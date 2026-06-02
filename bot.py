import time
import requests
import os
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = '5487451507'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 GOLG SNIPER BOT online!\nNo Updater. No Proxy. Just works!\nTry: /price or say Hi")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(requests.get("https://api.metals.live/v1/spot", timeout=10).json()[0]['gold'])
        await update.message.reply_text(f"💰 Gold: ${price:.2f}/oz")
    except:
        await update.message.reply_text("Price check failed")

async def chatback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yo! I'm alive 😎 Alerts working 24/7")

def send_telegram(msg):
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                  data={'chat_id': CHAT_ID, 'text': msg}, timeout=10)

def alert_loop():
    print("Bot running... Telegram alerts: ACTIVE ✅")
    send_telegram("🤖 Bot RESTARTED with fixed code!\nUpdater error is gone.")
    while True:
        time.sleep(600)

threading.Thread(target=alert_loop, daemon=True).start()

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", price))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatback))

print("Chat bot started...")
app.run_polling()

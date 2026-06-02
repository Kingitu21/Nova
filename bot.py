import time
import requests
import os
import threading
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = '5487451507'

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🚀 GOLG SNIPER BOT online!\nPTB v13 mode active\nTry: /price or say Hi")

def price(update: Update, context: CallbackContext):
    try:
        data = requests.get("https://api.metals.live/v1/spot", timeout=10).json()
        price = float(data['gold']) # Fixed: removed [0], API returns dict not list
        update.message.reply_text(f"💰 Gold: ${price:.2f}/oz")
    except Exception as e:
        update.message.reply_text(f"Price check failed: {e}")

def chatback(update: Update, context: CallbackContext):
    update.message.reply_text("Yo! I'm alive 😎 v13 Updater working")

def send_telegram(msg):
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                  data={'chat_id': CHAT_ID, 'text': msg}, timeout=10)

def alert_loop():
    print("Bot running... Telegram alerts: ACTIVE ✅")
    while True:
        time.sleep(600)

threading.Thread(target=alert_loop, daemon=True).start()

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("price", price))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, chatback))

print("Chat bot started...")
updater.start_polling()

# Moved startup message here - after polling starts
send_telegram("🤖 Bot RESTARTED with PTB v13!\nUpdater error fixed.")

updater.idle()

import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.environ.get("BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🚀 GOLG SNIPER BOT online!\n"
        "PTB v13 mode active\n"
        "Try: /price or say Hi"
    )

def price(update: Update, context: CallbackContext):
    try:
        response = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
        response.raise_for_status()
        data = response.json()
        gold_price = data["price"]
        update.message.reply_text(f"💰 Gold: ${gold_price:.2f}/oz\nUpdated: {data.get('timestamp', 'now')}")
    except Exception as e:
        update.message.reply_text(f"Price check failed:\n{e}")

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    if "hi" in text or "hello" in text:
        update.message.reply_text("Yo! I'm alive 😎 v13 Updater working")
    else:
        update.message.reply_text("Type /price for gold price")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("price", price))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    print("Bot started...")
    updater.idle()

if __name__ == "__main__":
    main()

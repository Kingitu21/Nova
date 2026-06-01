import time
import requests
import xml.etree.ElementTree as ET
from textblob import TextBlob
from datetime import datetime

# ====== YOUR SETTINGS ======
TELEGRAM_TOKEN = '8974789330:AAES4xR7YGJ9dGXrlC0iPVmspQqHC7BNbSg'
CHAT_ID = '5487451507'
GOLD_THRESHOLD = 2000  # Alert if gold price > $2000
PROXY = {'https': 'http://proxy.server:3128'}  # PythonAnywhere free proxy

# ====== FUNCTIONS ======
def get_gold_price():
    """Get current gold price"""
    try:
        url = "https://api.metals.live/v1/spot"
        r = requests.get(url, proxies=PROXY, timeout=10)
        data = r.json()
        return float(data[0]['gold'])
    except:
        return None

def get_gold_news():
    """Get gold news from Google News RSS - works with proxy"""
    try:
        url = "https://news.google.com/rss/search?q=gold+price&hl=en-US&gl=US&ceid=US:en"
        r = requests.get(url, proxies=PROXY, timeout=10)
        root = ET.fromstring(r.content)
        
        alerts = []
        for item in root.findall('.//item')[:3]:  # Top 3 news
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
    """Send to Telegram via proxy"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=data, proxies=PROXY, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

# ====== MAIN LOOP ======
print("Bot running... Telegram alerts: ACTIVE ✅")
send_telegram("🤖 Gold Bot is LIVE!\nProxy fix applied. I'll alert you 24/7")

counter = 0
while True:
    try:
        # Check price every 10 min
        price = get_gold_price()
        if price and price > GOLD_THRESHOLD:
            msg = f"🚨 GOLD ALERT!\nPrice: ${price:.2f}\nAbove ${GOLD_THRESHOLD}"
            send_telegram(msg)
        
        # Check news every 30 min = 3 loops
        counter += 1
        if counter % 3 == 0:
            news_alerts = get_gold_news()
            for alert in news_alerts:
                send_telegram(alert)
        
        time.sleep(600)  # Wait 10 min
        
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
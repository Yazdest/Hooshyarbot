import os
from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route('/')
def home():
    return "Hooshyar Bot is active and running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    
    # بررسی اینکه پیام متنی وجود داشته باشد
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        
        # پاسخ مستقیم و آنی با درخواست HTTP به تلگرام
        if text == "/start" or text == "سلام":
            reply_text = "سلام! ربات هوشیار با موفقیت روی سرور ابری مستقر شد و آماده پاسخگویی است."
        else:
            reply_text = f"پیام شما دریافت شد: {text}"
            
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": reply_text
        }
        requests.post(url, json=payload)
        
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

import os
from flask import Flask, request
import requests
from google import genai

app = Flask(__name__)

TELEGRAM_TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# دریافت کلید API جمینای از تنظیمات سرور رندر
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

@app.route('/')
def home():
    return "Hooshyar AI Bot is active and running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
        # مقدار پیش‌فرض در صورت تنظیم نبودن کلید
        reply_text = "خطا: کلید هوش مصنوعی در سرور تنظیم نشده است."
        
        if client:
            try:
                # ارسال پیام کاربر به مدل هوش مصنوعی
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=user_text,
                )
                reply_text = response.text
            except Exception as e:
                # بررسی خطای ترافیک بالا یا ناپایداری موقت سرور گوگل
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    reply_text = "⚠️ سرور هوش مصنوعی در حال حاضر با ترافیک بالا مواجه است. لطفاً چند لحظه دیگر دوباره پیام بفرستید."
                else:
                    reply_text = f"متأسفم، در پردازش درخواست شما خطایی رخ داد."
        
        # ارسال پاسخ هوشمند به تلگرام
        payload = {
            "chat_id": chat_id,
            "text": reply_text
        }
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
        
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

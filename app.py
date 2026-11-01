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

# لیست مدل‌ها به ترتیب اولویت برای سوییچ خودکار در صورت بروز خطا
FALLBACK_MODELS = ['gemini-3.8-flash', 'gemini-2.5-flash', 'gemini-1.5-flash']

@app.route('/')
def home():
    return "Hooshyar AI Bot is active and running with Multi-Model Fallback!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
        reply_text = "خطا: کلید هوش مصنوعی در سرور تنظیم نشده است."
        
        if client:
            success = False
            # حلقه برای تلاش بین مدل‌های مختلف به صورت خودکار
            for model_name in FALLBACK_MODELS:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=user_text,
                    )
                    reply_text = response.text
                    success = True
                    break  # اگر پاسخ با موفقیت دریافت شد، از حلقه خارج شو
                except Exception as e:
                    # اگر خطایی رخ داد، به مدل بعدی سوییچ کن
                    continue
            
            # اگر هیچ‌کدام از مدل‌ها پاسخ ندادند
            if not success:
                reply_text = "⚠️ تمامی مدل‌های هوش مصنوعی در حال حاضر با ترافیک بالا مواجه هستند. لطفاً چند لحظه دیگر دوباره پیام بفرستید."
        
        # ارسال پاسخ هوشمند به تلگرام
        payload = {
            "chat_id": chat_id,
            "text": reply_text
        }
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
        
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

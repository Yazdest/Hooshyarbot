import os
from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route('/')
def home():
    return "Hooshyar AI Bot Model Inspector is active!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
        if not GROQ_API_KEY:
            reply_text = "خطا: کلید GROQ_API_KEY تنظیم نشده است!"
        else:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            try:
                # درخواست مستقیم لیست مدل‌های مجاز این کلید خاص
                res = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=10)
                
                if res.status_code == 200:
                    models_json = res.json()
                    model_ids = [m.get("id") for m in models_json.get("data", [])]
                    reply_text = f"📋 مدل‌های مجاز کلید شما:\n" + "\n".join(model_ids[:10])
                else:
                    reply_text = f"خطا در دریافت لیست مدل‌ها (کد {res.status_code}):\n{res.text}"
            except Exception as e:
                reply_text = f"خطای اتصال: {str(e)}"
        
        # ارسال لیست به تلگرام
        payload_telegram = {
            "chat_id": chat_id,
            "text": reply_text
        }
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload_telegram)
        
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

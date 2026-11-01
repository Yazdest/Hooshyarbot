import os
from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# دریافت کلید API گروک از تنظیمات سرور رندر
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route('/')
def home():
    return "Hooshyar AI Bot Debug Mode is active!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
        if not GROQ_API_KEY:
            reply_text = "خطا: کلید GROQ_API_KEY در تنظیمات Render وارد نشده است!"
        else:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # استفاده از مدل استاندارد گروک
            payload_groq = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "user", "content": user_text}
                ]
            }
            
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    json=payload_groq,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    res_json = response.json()
                    reply_text = res_json['choices'][0]['message']['content']
                else:
                    # چاپ دقیق متن خطای بازگشتی از سرور گروک برای عیب‌یابی
                    reply_text = f"⚠️ خطای سرور گروک (کد {response.status_code}):\n{response.text}"
            except Exception as e:
                reply_text = f"❌ خطای اتصال فنی: {str(e)}"
        
        # ارسال پاسخ نهایی به تلگرام
        payload_telegram = {
            "chat_id": chat_id,
            "text": reply_text
        }
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload_telegram)
        
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

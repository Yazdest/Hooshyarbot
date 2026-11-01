import os
from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# دریافت کلید API گروک از تنظیمات سرور رندر
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# لیست کامل مدل‌های احتمالی گروک برای جلوگیری صددرصدی از خطای مدل
CANDIDATE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "gemma2-9b-it"
]

@app.route('/')
def home():
    return "Hooshyar AI Bot is active and stable!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
        reply_text = "خطا: کلید هوش مصنوعی در سرور تنظیم نشده است."
        
        if GROQ_API_KEY:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            success = False
            # حلقه هوشمند روی تمام مدل‌های ممکن گروک
            for model_name in CANDIDATE_MODELS:
                payload_groq = {
                    "model": model_name,
                    "messages": [
                        {"role": "user", "content": user_text}
                    ]
                }
                
                try:
                    response = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        json=payload_groq,
                        headers=headers,
                        timeout=12
                    )
                    
                    if response.status_code == 200:
                        res_json = response.json()
                        reply_text = res_json['choices'][0]['message']['content']
                        success = True
                        break # اگر پاسخ گرفتیم، از حلقه خارج شو
                except Exception:
                    continue
            
            if not success:
                reply_text = "متأسفم، در حال حاضر ارتباط با سرور هوش مصنوعی برقرار نشد. لطفاً چند لحظه دیگر دوباره تلاش کنید."
        
        # ارسال پاسخ نهایی به تلگرام
        payload_telegram = {
            "chat_id": chat_id,
            "text": reply_text
        }
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload_telegram)
        
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

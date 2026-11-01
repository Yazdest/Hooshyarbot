import os
from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route('/')
def home():
    return "Hooshyar AI Bot Dynamic Model Discovery is active!"

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
                # ۱. گرفتن لیست مدل‌های مجاز برای این کلید خاص به صورت مستقیم
                models_res = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=10)
                
                target_model = "llama3-70b-8192" # پیش‌فرض امن
                
                if models_res.status_code == 200:
                    models_data = models_res.json().get("data", [])
                    # پیدا کردن اولین مدلی که مربوط به چت است
                    for m in models_data:
                        m_id = m.get("id", "")
                        if "llama" in m_id or "gemma" in m_id or "mixtral" in m_id:
                            target_model = m_id
                            break
                
                # ۲. ارسال درخواست چت با مدل پیدا شده
                payload_groq = {
                    "model": target_model,
                    "messages": [
                        {"role": "user", "content": user_text}
                    ]
                }
                
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
                    reply_text = f"خطا با مدل {target_model} (کد {response.status_code}):\n{response.text}"
            except Exception as e:
                reply_text = f"خطای سیستمی: {str(e)}"
        
        # ارسال پاسخ نهایی به تلگرام
        payload_telegram = {
            "chat_id": chat_id,
            "text": reply_text
        }
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload_telegram)
        
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

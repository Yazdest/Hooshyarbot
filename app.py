import os
from flask import Flask, request
import requests
from groq import Groq

app = Flask(__name__)

TELEGRAM_TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# دریافت کلید API گروک از تنظیمات سرور رندر
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

@app.route('/')
def home():
    return "Hooshyar AI Bot is active with Dynamic Model Detection!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
        reply_text = "خطا: کلید هوش مصنوعی گروک در سرور تنظیم نشده است."
        
        if client:
            try:
                # ۱. دریافت لیست مدل‌های فعال حساب شما به صورت خودکار از خود گروک
                models_response = client.models.list()
                available_models = [m.id for m in models_response.data if "llama" in m.id or "mixtral" in m.id or "gemma" in m.id]
                
                # اگر لیستی پیدا شد، مدل اول را انتخاب کن، وگرنه یک پیش‌فرض مطمئن بگذار
                model_to_use = available_models[0] if available_models else "llama-3.3-70b-versatile"
                
                # ۲. ارسال پیام به مدل شناسایی‌شده
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": user_text,
                        }
                    ],
                    model=model_to_use,
                )
                reply_text = chat_completion.choices[0].message.content
                
            except Exception as e:
                # ۳. اگر به هر دلیلی لیست‌گیری خطا داد، از مدل‌های امن و عمومی پشتیبان استفاده کن
                fallback_defaults = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"]
                success = False
                for fb_model in fallback_defaults:
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": user_text}],
                            model=fb_model,
                        )
                        reply_text = chat_completion.choices[0].message.content
                        success = True
                        break
                    except:
                        continue
                
                if not success:
                    reply_text = f"متأسفم، خطایی در ارتباط با هوش مصنوعی رخ داد: {str(e)}"
        
        # ارسال پاسخ نهایی به تلگرام
        payload = {
            "chat_id": chat_id,
            "text": reply_text
        }
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
        
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

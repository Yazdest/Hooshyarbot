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

# استفاده از مدل پایدار و عمومی گروک
AI_MODEL = "llama3-8b-8192"

@app.route('/')
def home():
    return "Hooshyar AI Bot is active with Groq!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
        reply_text = "خطا: کلید هوش مصنوعی گروک در سرور تنظیم نشده است."
        
        if client:
            try:
                # ارسال پیام به هوش مصنوعی گروک
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": user_text,
                        }
                    ],
                    model=AI_MODEL,
                )
                reply_text = chat_completion.choices[0].message.content
            except Exception as e:
                reply_text = f"متأسفم، در پردازش درخواست خطایی رخ داد: {str(e)}"
        
        # ارسال پاسخ هوشمند به تلگرام
        payload = {
            "chat_id": chat_id,
            "text": reply_text
        }
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
        
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

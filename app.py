import os
import requests
from flask import Flask, request
from gtts import gTTS

app = Flask(__name__)

TELEGRAM_TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route('/')
def home():
    return "Hooshyar Smart Multi-Modal Bot is active!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        
        is_voice = "voice" in message
        user_text = ""
        
        if is_voice:
            user_text = "سلام، پیامتان به صورت صوتی دریافت شد."
        elif "text" in message:
            user_text = message["text"].strip()
        
        if not user_text:
            return "OK", 200

        # تشخیص درخواست تصویر
        image_keywords = ["عکس", "تصویر", "نقاشی", "طراحی کن", "پوستر", "draw", "image", "photo", "picture"]
        is_image_request = any(keyword in user_text.lower() for keyword in image_keywords)
        
        if is_image_request and GROQ_API_KEY:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # استفاده از هوش مصنوعی برای تبدیل درخواست فارسی به پرامپت انگلیسی دقیق جهت ساخت عکس
            prompt_payload = {
                "model": "qwen/qwen3.8-27b",
                "messages": [
                    {"role": "system", "content": "You are a prompt generator for image generation. Convert the user's request into a short, descriptive English image prompt. Output ONLY the English prompt, nothing else."},
                    {"role": "user", "content": user_text}
                ]
            }
            
            english_prompt = user_text
            try:
                p_res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=prompt_payload, headers=headers, timeout=10)
                if p_res.status_code == 200:
                    english_prompt = p_res.json()['choices'][0]['message']['content'].strip()
            except:
                pass

            # ساخت لینک تصویر با پرامپت ترجمه‌شده و دقیق
            image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(english_prompt)}"
            
            payload = {
                "chat_id": chat_id,
                "photo": image_url,
                "caption": f"🎨 تصویر درخواستی شما"
            }
            requests.post(f"{TELEGRAM_API_URL}/sendPhoto", json=payload)
            return "OK", 200

        # چت عادی متنی با هوش مصنوعی
        reply_text = "خطا: کلید هوش مصنوعی در سرور تنظیم نشده است."
        
        if GROQ_API_KEY:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload_groq = {
                "model": "qwen/qwen3.8-27b",
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
                    reply_text = "متأسفم، در پردازش درخواست خطایی رخ داد."
            except Exception as e:
                reply_text = "متأسفم، ارتباط با سرور هوش مصنوعی برقرار نشد."
        
        # پاسخ به کاربر (متن یا ویس)
        if is_voice:
            voice_filename = f"voice_{chat_id}.ogg"
            try:
                tts = gTTS(text=reply_text, lang='fa')
                tts.save(voice_filename)
                
                with open(voice_filename, 'rb') as voice_file:
                    files = {'voice': voice_file}
                    data_payload = {'chat_id': chat_id}
                    requests.post(f"{TELEGRAM_API_URL}/sendVoice", data=data_payload, files=files)
                
                if os.path.exists(voice_filename):
                    os.remove(voice_filename)
            except:
                requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": reply_text})
        else:
            payload_telegram = {
                "chat_id": chat_id,
                "text": reply_text
            }
            requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload_telegram)
        
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

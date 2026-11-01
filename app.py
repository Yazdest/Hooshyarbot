import os
import requests
from flask import Flask, request
from gtts import gTTS

app = Flask(__name__)

TELEGRAM_TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# حافظه موقت برای نگهداری آخرین درخواست تصویر هر کاربر (جهت قابلیت ویرایش و حافظه تصویر)
user_last_prompts = {}

@app.route('/')
def home():
    return "Hooshyar Ultimate Smart Bot is active!"

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

        # تشخیص هوشمند درخواست تصویر یا ویرایش عکس قبلی
        image_keywords = ["عکس", "تصویر", "نقاشی", "طراحی", "پوستر", "بکش", "برف", "اضافه کن", "رنگ", "draw", "image", "photo", "picture"]
        is_image_request = any(keyword in user_text.lower() for keyword in image_keywords) or chat_id in user_last_prompts
        
        if is_image_request and GROQ_API_KEY:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # بازیابی زمینه یا عکس قبلی کاربر برای حفظ حافظه مکالمه تصویری
            previous_context = user_last_prompts.get(chat_id, "")
            
            system_prompt = (
                "You are an advanced AI image prompt engineer. Your task is to create a highly detailed, "
                "high-quality English prompt for image generation using Flux model. "
                f"Previous image context: '{previous_context}'. "
                "If the user's current message is a modification or addition (e.g. adding snow, changing background), update the previous context accordingly. "
                "Output ONLY the final, detailed English prompt for the image, nothing else."
            )
            
            prompt_payload = {
                "model": "qwen/qwen3.8-27b",
                "messages": [
                    {"role": "system", "content": system_prompt},
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
            
            # ذخیره پرامپت جدید در حافظه موقت کاربر
            user_last_prompts[chat_id] = english_prompt

            # استفاده از مدل فوق‌العاده باکیفیت و قدرتمند Flux با رزولوشن بالا
            image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(english_prompt)}?model=flux&width=1024&height=1024&nologo=true"
            
            payload = {
                "chat_id": chat_id,
                "photo": image_url,
                "caption": f"🎨 تصویر باکیفیت درخواستی شما"
            }
            requests.post(f"{TELEGRAM_API_URL}/sendPhoto", json=payload)
            return "OK", 200

        # چت عادی متنی با مدل هوش مصنوعی Qwen
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
        
        # پاسخ هوشمند: اگر کاربر ویس فرستاده بود ویس بده، اگر متن فرستاده بود متن بده
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

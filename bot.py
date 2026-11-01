import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"
OPENROUTER_API_KEY = "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"
GROQ_API_KEY = "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"

async def ask_ai(prompt_text):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://telegram.org",
        "X-Title": "Hooshyar Bot"
    }
    
    payload = {
        "model": "google/gemini-2.5-flash",
        "messages": [
            {"role": "system", "content": "شما «هوشیار» هستید؛ یک دستیار هوشمند، بسیار دانا، مؤدب و حرفه‌ای به زبان فارسی."},
            {"role": "user", "content": prompt_text}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
        res_data = response.json()
        if 'choices' in res_data and len(res_data['choices']) > 0:
            return res_data['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"AI Error: {e}")
    
    return "متأسفانه در پردازش درخواست خطایی رخ داد."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.message.chat_id
    
    await context.bot.send_message(chat_id=chat_id, text="هوشیار در حال پردازش متن شماست...")
    ai_reply = await ask_ai(user_text)
    await context.bot.send_message(chat_id=chat_id, text=ai_reply)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await context.bot.send_message(chat_id=chat_id, text="هوشیار در حال گوش دادن و تبدیل ویس شماست...")

    try:
        voice_file = await update.message.voice.get_file()
        file_path = "voice.ogg"
        await voice_file.download_to_drive(file_path)

        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
        
        with open(file_path, "rb") as audio_file:
            files = {"file": (file_path, audio_file, "audio/ogg")}
            data = {"model": "whisper-large-v3", "language": "fa"}
            response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        
        if os.path.exists(file_path):
            os.remove(file_path)

        res_json = response.json()
        if "text" in res_json:
            transcribed_text = res_json["text"]
            await context.bot.send_message(chat_id=chat_id, text=f"🗣 متن شما: {transcribed_text}")
            ai_reply = await ask_ai(transcribed_text)
            await context.bot.send_message(chat_id=chat_id, text=ai_reply)
        else:
            await context.bot.send_message(chat_id=chat_id, text="متأسفانه نتوانستم ویس شما را به متن تبدیل کنم.")

    except Exception as e:
        logging.error(f"Voice Error: {e}")
        await context.bot.send_message(chat_id=chat_id, text="خطایی در پردازش پیام صوتی رخ داد.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    print("ربات پیشرفته «هوشیار» با قابلیت صوت و متن روشن شد...")
    application.run_polling()
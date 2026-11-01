import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

app = Flask(__name__)

TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"

# ساخت و راه‌اندازی ربات
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("سلام! ربات هوشیار با موفقیت روی سرور ابری مستقر شد.")

application.add_handler(CommandHandler("start", start))

# راه‌اندازی اولیه اپلیکیشن تلگرام
loop = asyncio.get_event_loop()
loop.run_until_complete(application.initialize())

@app.route('/')
def home():
    return "Hooshyar Bot is active and running!"

# تغییر مسیر وب‌هوک به یک مسیر ثابت و ساده (/webhook)
@app.route('/webhook', methods=['POST'])
def webhook():
    json_data = request.get_json(force=True)
    update = Update.de_json(json_data, application.bot)
    
    async def process():
        await application.process_update(update)
        
    loop.run_until_complete(process())
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

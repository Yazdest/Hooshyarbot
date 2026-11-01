import os
import threading
from flask import Flask
from telegram.ext import Application, CommandHandler

# ۱. راه‌اندازی وب‌سرور Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Hooshyar Bot is active and running!"

# ۲. تابع اجرای ربات تلگرام
def run_bot():
    TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"
    application = Application.builder().token(TOKEN).build()
    
    async def start(update, context):
        await update.message.reply_text("سلام! ربات هوشیار با موفقیت روی سرور ابری مستقر شد.")
        
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

# اجرای ربات در ترد پس‌زمینه به محض لود شدن برنامه توسط Gunicorn
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

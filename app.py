import os
import threading
from flask import Flask
from telegram.ext import Application, CommandHandler

# ۱. راه‌اندازی وب‌سرور Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Hooshyar Bot is active and running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# ۲. اجرای وب‌سرور در ترد پس‌زمینه
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# ۳. اجرای ربات تلگرام در ترد اصلی (اصلی‌ترین بخش برای رفع خطا)
def main():
    TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"
    application = Application.builder().token(TOKEN).build()
    
    async def start(update, context):
        await update.message.reply_text("سلام! ربات هوشیار با موفقیت روی سرور ابری مستقر شد.")
        
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == "__main__":
    main()

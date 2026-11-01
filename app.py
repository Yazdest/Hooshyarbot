import os
import threading
from flask import Flask
from telegram.ext import Application, CommandHandler

# ۱. راه‌اندازی وب‌سرور سبک Flask برای پاسخ به پورت رندر
app = Flask(__name__)

@app.route('/')
def home():
    return "Hooshyar Bot is active and running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ۲. توابع مربوط به ربات تلگرام «هوشیار»
async def start(update, context):
    await update.message.reply_text("سلام! ربات هوشیار با موفقیت روی سرور ابری مستقر شد.")

def main():
    # توکن صحیح ربات شما
    TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"
    
    application = Application.builder().token(TOKEN).build()
    
    # اضافه کردن دستورات ربات
    application.add_handler(CommandHandler("start", start))
    
    # شروع به کار ربات (Polling)
    application.run_polling()

if __name__ == "__main__":
    # اجرای وب‌سرور Flask در پس‌زمینه (برای جلوگیری از خطای پورت رندر)
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # اجرای ربات تلگرام در ترد اصلی
    main()

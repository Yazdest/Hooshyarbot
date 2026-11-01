import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

app = Flask(__name__)

TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"

# ساخت و راه‌اندازی اولیه اپلیکیشن ربات
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("سلام! ربات هوشیار با موفقیت روی سرور ابری مستقر شد.")

application.add_handler(CommandHandler("start", start))

@app.route('/')
def home():
    return "Hooshyar Bot is active and running via Webhook!"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_data = request.get_json(force=True)
        update = Update.de_json(json_data, application.bot)
        
        # استفاده از متد مناسب برای پردازش آپدیت در بستر وب‌هوک
        async def main():
            await application.initialize()
            await application.process_update(update)

        import asyncio
        asyncio.run(main())
        return "OK", 200
    else:
        return "Invalid Request", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

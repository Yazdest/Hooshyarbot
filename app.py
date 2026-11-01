import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler

app = Flask(__name__)

TOKEN = "9050811861:AAH1_RI-0Vo6CzzOmJQogRxvLaNO6j6f5hM"

application = None

def get_application():
    global application
    if application is None:
        application = Application.builder().token(TOKEN).build()
        
        async def start(update: Update, context):
            await update.message.reply_text("سلام! ربات هوشیار با موفقیت روی سرور ابری مستقر شد.")
            
        application.add_handler(CommandHandler("start", start))
    return application

@app.route('/')
def home():
    return "Hooshyar Bot is active and running via Webhook!"

@app.route('/webhook', methods=['POST'])
def webhook():
    json_data = request.get_json(force=True)
    app_instance = get_application()
    
    async def process():
        if not app_instance.initialized:
            await app_instance.initialize()
        update = Update.de_json(json_data, app_instance.bot)
        await app_instance.process_update(update)
        
    asyncio.run(process())
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

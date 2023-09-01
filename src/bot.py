import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram import Update

from config.config import tg_settings

load_dotenv()

TELEGRAM_BOT_TOKEN = tg_settings.BOT_TOKEN


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"/start by user_id: {update.effective_chat.id}")
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='Bot is activated')


async def sendDoc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    document = ''
    await context.bot.send_document(chat_id, document)


application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

application.add_handler(CommandHandler('start', start))

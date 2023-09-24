from telegram import Update, CallbackQuery
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from cleaning_regulations import start, button, photo

# Обработчики
start_handler = CommandHandler("start", start)
button_handler = CallbackQueryHandler(button)
photo_handler = MessageHandler(Filters.photo, photo)

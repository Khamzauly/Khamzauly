from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import logging
import os

# Инициализация логгера
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен вашего бота
TOKEN = os.getenv("TOKEN")

tasks = {
    "Task 1": {"status": "Not Done", "worker": None},
    "Task 2": {"status": "Not Done", "worker": None},
    # Добавьте дополнительные задачи по необходимости
}

def start(update: Update, _: CallbackContext) -> None:
    keyboard = []
    for task, info in tasks.items():
        keyboard.append([InlineKeyboardButton(f"{task} - {info['status']}", callback_data=task)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose a task:", reply_markup=reply_markup)

def button(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    task = query.data
    tasks[task]["status"] = "Done"
    tasks[task]["worker"] = query.from_user.id
    query.edit_message_text(text=f"{task} is now Done by {query.from_user.id}")

def main():
    updater = Updater(token=TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

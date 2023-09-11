from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import logging

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
        emoji = "✅" if info['status'] == "Done" else ""
        keyboard.append([InlineKeyboardButton(f"{task} {emoji}", callback_data=task)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose a task:", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    task = query.data
    tasks[task]["status"] = "Done"
    tasks[task]["worker"] = query.from_user.id
    
    keyboard = []
    for task, info in tasks.items():
        emoji = "✅" if info['status'] == "Done" else ""
        keyboard.append([InlineKeyboardButton(f"{task} {emoji}", callback_data=task)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text("Choose a task:", reply_markup=reply_markup)

def main():
    updater = Updater(token=TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

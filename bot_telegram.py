from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import os

TOKEN = os.getenv("TOKEN")

tasks = {
    "Task 1": {"status": "Not Done", "worker": None},
    "Task 2": {"status": "Not Done", "worker": None},
    # ...
}

def start(update: Update, _: CallbackContext) -> None:
    keyboard = []
    for task in tasks:
        keyboard.append([InlineKeyboardButton(task, callback_data=task)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose a task:", reply_markup=reply_markup)

def button(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    task = query.data
    tasks[task]["status"] = "Done"
    tasks[task]["worker"] = query.from_user.id
    query.edit_message_text(text=f"{task} is now Done by {query.from_user.id}")

updater = Updater(TOKEN)

updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()

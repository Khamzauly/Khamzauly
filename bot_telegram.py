from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import os

TOKEN = os.getenv("TOKEN")

tasks = {f"Task {i+1}": {"status": "Not Done", "worker": None} for i in range(25)}
active_chats = set()  # Здесь будем хранить активные чаты

def start(update: Update, _: CallbackContext) -> None:
    chat_id = update.message.chat_id
    active_chats.add(chat_id)
    keyboard = generate_keyboard()
    update.message.reply_text("Choose a task:", reply_markup=keyboard)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    task = query.data
    tasks[task]["status"] = "Done"
    tasks[task]["worker"] = query.from_user.first_name

    keyboard = generate_keyboard()

    for chat_id in active_chats:
        context.bot.send_message(chat_id, "Tasks updated!", reply_markup=keyboard)

def generate_keyboard():
    keyboard = []
    for task, data in tasks.items():
        text = task
        if data["status"] == "Done":
            text += f" ✅ by {data['worker']}"
        keyboard.append([InlineKeyboardButton(text, callback_data=task)])
    return InlineKeyboardMarkup(keyboard)

def main():
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import os

TOKEN = os.getenv("TOKEN")

tasks = {f"Task {i+1}": {"status": "Not Done", "worker": None} for i in range(25)}
active_chats = {}  # Здесь будем хранить активные чаты и ID сообщений

def start(update: Update, _: CallbackContext) -> None:
    chat_id = update.message.chat_id
    keyboard = generate_keyboard()
    sent_message = update.message.reply_text("Choose a task:", reply_markup=keyboard)
    active_chats[chat_id] = sent_message.message_id  # Сохраняем ID сообщения

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    task = query.data
    tasks[task]["status"] = "Done"
    tasks[task]["worker"] = query.from_user.first_name

    keyboard = generate_keyboard()

    for chat_id, message_id in active_chats.items():
        context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Updated tasks:", reply_markup=keyboard)

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

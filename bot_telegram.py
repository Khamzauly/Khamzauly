from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import logging
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")

tasks = {f"Task {i+1}": {"status": "Not Done", "worker": None} for i in range(25)}

# Список для хранения пар (chat_id, message_id)
chat_message_ids = []

def generate_keyboard():
    keyboard = []
    for task, info in tasks.items():
        emoji = f"✅ by {info['worker']}" if info['status'] == "Done" else ""
        keyboard.append([InlineKeyboardButton(f"{task} {emoji}", callback_data=task)])
    return InlineKeyboardMarkup(keyboard)

def start(update: Update, _: CallbackContext) -> None:
    reply_markup = generate_keyboard()
    sent_message = update.message.reply_text("Choose a task:", reply_markup=reply_markup)
    
    # Добавляем пару (chat_id, message_id) в список
    chat_message_ids.append((update.message.chat_id, sent_message.message_id))

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    task = query.data
    tasks[task]["status"] = "Done"
    tasks[task]["worker"] = query.from_user.first_name

    reply_markup = generate_keyboard()
    
    # Обновляем сообщение для пользователя, который выполнил задачу
    query.edit_message_text("Choose a task:", reply_markup=reply_markup)
    
    # Обновляем сообщения для всех остальных пользователей
    for chat_id, message_id in chat_message_ids:
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Choose a task:",
            reply_markup=reply_markup
        )

def main():
    updater = Updater(token=TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import os

# Устанавливаем переменные окружения и настройки
TOKEN = os.getenv("TOKEN")
json_str = os.getenv("LINK")
scopes = ['https://www.googleapis.com/auth/spreadsheets']

# Инициализируем Google Sheets API
google_credentials = json.loads(json_str)
credentials = Credentials.from_service_account_info(google_credentials, scopes=scopes)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

# Инициализируем некоторые переменные
zone_photos = {}
photo_zones = ["зоны 1", "зоны 2", "зоны 3"]

def get_tasks():
    result = sheet.values().get(spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w", range="asd!A2:D32").execute()
    return result.get('values', [])

def update_task(row, user_name):
    # Обновляем задачу в Google Sheets
    sheet.values().update(
        spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w",
        range=f"asd!B{row}:D{row}",
        body={"values": [[True, user_name, str(datetime.now())]]},
        valueInputOption="RAW"
    ).execute()

def all_tasks_done():
    # Проверяем, все ли задачи выполнены
    tasks = get_tasks()
    return all(len(task) >= 2 and task[1] == "TRUE" for task in tasks)

def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton(f"{task[0]} {'✅' if task[1] == 'TRUE' else '❌'}", callback_data=str(i))]
                for i, task in enumerate(get_tasks())]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите задачу:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    task_index = int(query.data)
    user_name = update.effective_user.first_name

    update_task(task_index + 2, user_name)  # Обновляем данные в Google Sheets

    # Обновляем клавиатуру в сообщении
    new_keyboard = [[InlineKeyboardButton(f"{task[0]} {'✅' if task[1] == 'TRUE' else '❌'}", callback_data=str(i))]
                    for i, task in enumerate(get_tasks())]
    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(new_keyboard))

    if all_tasks_done():
        context.bot.send_message(chat_id=update.effective_chat.id, text="Уборка закончена. Спасибо!")
        # Здесь можно добавить вашу логику для фото

def photo(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    photo_file = context.bot.getFile(update.message.photo[-1].file_id)
    photo_file.download(f"photo_{user_id}.jpg")
    # Добавьте вашу логику для работы с фото

# Основной код
updater = Updater(TOKEN)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button))
dp.add_handler(MessageHandler(Filters.photo, photo))

updater.start_polling()
updater.idle()

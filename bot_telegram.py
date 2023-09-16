from telegram import Update, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputFile, Bot, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from current_time import get_current_date_in_gmt6
from io import BytesIO
import requests
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime, date
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
current_photo_zone = None  # Добавим глобальную переменную для текущей фотозоны
photo_zones = ["зоны 1", "зоны 2", "зоны 3"]

Date = get_current_date_in_gmt6()

def get_tasks():
    result = sheet.values().get(spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w", range="temp_evening!A4:B100").execute()
    return result.get('values', [])

def update_task(row, user_name):
    # Обновляем задачу в Google Sheets
    sheet.values().update(
        spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w",
        range=f"temp_evening!B{row}:D{row}",
        body={"values": [[True, user_name, str(Date)]]},
        valueInputOption="RAW"
    ).execute()

def all_tasks_done():
    # Проверяем, все ли задачи выполнены
    tasks = get_tasks()
    return all(len(task) >= 2 and task[1] == "TRUE" for task in tasks)

# Для хранения пар "Chat ID - Имя"
chat_names = {}

def load_chat_names():
    global chat_names
    result = sheet.values().get(spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w", range="чаты!A:B").execute()
    values = result.get('values', [])
    chat_names = {str(row[1]): row[0] for row in values if len(row) > 1}

load_chat_names()


def start(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)
    if chat_id in chat_names:
        name = chat_names[chat_id]
        update.message.reply_text(f'Ассаляму алейкум, {name}!')
    else:
        update.message.reply_text('Ассаляму алейкум!')
    try:
        keyboard = [
            [InlineKeyboardButton(f"{task[0]} {'✅' if len(task) > 1 and task[1] == 'TRUE' else '❌'}", callback_data=str(i))]
            for i, task in enumerate(get_tasks()) if len(task) > 0
        ]
    except IndexError as e:
        print(f"An error occurred: {e}")

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите задачу:', reply_markup=reply_markup)



def button(update: Update, context: CallbackContext):
    query = update.callback_query
    task_index = int(query.data)
    user_name = update.effective_user.first_name

    update_task(task_index + 4, user_name)  # Обновляем данные в Google Sheets

    # Обновляем клавиатуру в сообщении
    new_keyboard = [[InlineKeyboardButton(f"{task[0]} {'✅' if task[1] == 'TRUE' else '❌'}", callback_data=str(i))]
        for i, task in enumerate(get_tasks())]
    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(new_keyboard))

    if all_tasks_done():
        context.bot.send_message(chat_id=update.effective_chat.id, text="Уборка закончена. Спасибо!")
        ask_for_photo(update.effective_chat.id, context, photo_zones[0])


def ask_for_photo(chat_id, context, zone):
    global current_photo_zone
    current_photo_zone = zone
    context.bot.send_message(chat_id=chat_id, text=f"Отправьте фотографию {zone}")

def photo(update: Update, context: CallbackContext):
    global current_photo_zone
    user_id = update.effective_user.id
    if not current_photo_zone:
        return

    photo_file = context.bot.getFile(update.message.photo[-1].file_id)
    response = requests.get(photo_file.file_path)
    zone_photos[current_photo_zone] = BytesIO(response.content)

    if current_photo_zone == photo_zones[-1]:
        send_photos_to_other_bot(zone_photos)
        current_photo_zone = None
    else:
        next_zone = photo_zones[photo_zones.index(current_photo_zone) + 1]
        ask_for_photo(update.effective_chat.id, context, next_zone)

def send_photos_to_other_bot(photos):
    BOT2_TOKEN = os.getenv("SECOND_BOT")
    CHAT_ID = os.getenv("CHAT_ID")
    bot2 = Bot(BOT2_TOKEN)

    media_group = []
    
    for zone, photo_stream in photos.items():
        photo_stream.seek(0)  # Возврат к началу потока
        media = InputMediaPhoto(media=photo_stream, caption=f"Фото {zone}")
        media_group.append(media)

    # Отправить текст перед группой фотографий
    bot2.send_message(chat_id=CHAT_ID, text=f"Смена за {date.today()} завершена.")
    
    # Отправить группу фотографий
    bot2.send_media_group(chat_id=CHAT_ID, media=media_group)

# Основной код
updater = Updater(TOKEN)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button))
dp.add_handler(MessageHandler(Filters.photo, photo))

updater.start_polling()
updater.idle()

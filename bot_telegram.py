from telegram import Update, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputFile, Bot, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from current_time import get_current_date_in_gmt6
from io import BytesIO
import requests
import logging
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

def get_date_from_sheet():
    result = sheet.values().get(spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w", range="temp_evening!B2").execute()
    values = result.get('values', [])
    if len(values) > 0 and len(values[0]) > 0:
        return values[0][0]
    return None


def get_tasks():
    result = sheet.values().get(spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w", range="temp_evening!A4:B100").execute()
    return result.get('values', [])

def update_task(row, user_name):
    # Обновляем задачу в Google Sheets
    sheet.values().update(
        spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w",
        range=f"temp_evening!B{row}:D{row}",
        body={"values": [[True, user_name, str(get_current_date_in_gmt6())]]},
        valueInputOption="RAW"
    ).execute()

def all_tasks_done():
    # Проверяем, все ли задачи выполнены
    tasks = get_tasks()
    return all(len(task) >= 2 and task[1] == "TRUE" for task in tasks)

chat_names = {}

def load_chat_names():
    global chat_names
    chat_names = {}
    result = sheet.values().get(spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w", range="чаты!A:B").execute()
    values = result.get('values', [])
    chat_names = {str(row[1]): str(row[0]) for row in values if len(row) > 1}

active_shift_users = []
active_messages = {} 

def update_all_chats(context: CallbackContext):
    logging.info(f"Trying to update all chats. Current active_shift_users: {active_shift_users}")
    logging.info(f"Current active_messages: {active_messages}")


    new_keyboard = [
        [InlineKeyboardButton(f"{task[0]} {'✅' if task[1] == 'TRUE' else '❌'}", callback_data=str(i))]
        for i, task

    for chat_id in active_shift_users:
        message_ids = active_messages.get(chat_id, [])  # Получаем список message_id для этого chat_id
        for message_id in message_ids:  # Проходим по всем message_id этого chat_id
            context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id,
                                                   reply_markup=InlineKeyboardMarkup(new_keyboard))


shift_status = {}

def load_shift_status():
    global shift_status
    result = sheet.values().get(spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w", range="чаты!A:C").execute()
    values = result.get('values', [])
    shift_status = {str(row[1]): str(row[2]) for row in values if len(row) > 2}

def start(update: Update, context: CallbackContext):
    load_chat_names()
    load_shift_status()
    chat_id = str(update.effective_chat.id)
    new_shift_status = shift_status.get(chat_id, "не определено")

    if chat_id not in chat_names:
        update.message.reply_text(f'Извините, у вас нет доступа к этому боту. Ваш чат id: {chat_id}. Запросите доступ у управляющего.')
        return
    elif chat_id in chat_names and new_shift_status != 'смена':
        update.message.reply_text('Извините, сейчас не ваша смена.')
        return
    elif chat_id in chat_names and new_shift_status == "смена":
        if chat_id not in active_shift_users:
            active_shift_users.append(chat_id)
        name = chat_names[chat_id]
        update.message.reply_text(f'Ассаляму алейкум, {name}!')

    if all_tasks_done():
        update.message.reply_text('Еще не время уборки')
        return  # Выход из функции, чтобы не выводить клавиатуру с задачами
    
    try:
        keyboard = [
            [InlineKeyboardButton(f"{task[0]} {'✅' if len(task) > 1 and task[1] == 'TRUE' else '❌'}", callback_data=str(i))]
            for i, task in enumerate(get_tasks()) if len(task) > 0
        ]
    except IndexError as e:
        print(f"An error occurred: {e}")

    reply_markup = InlineKeyboardMarkup(keyboard)
    sent_message = update.message.reply_text('Выберите задачу:', reply_markup=reply_markup)
    message_id = sent_message.message_id
    if chat_id not in active_messages:
        active_messages[chat_id] = []
    active_messages[chat_id].append(sent_message.message_id)


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    task_index = int(query.data)
    chat_id = str(update.effective_chat.id)
    user_name = chat_names.get(chat_id, "Неизвестный")

    update_task(task_index + 4, user_name)  # Обновляем данные в Google Sheets

    # Обновляем клавиатуру в сообщении
    new_keyboard = [
        [InlineKeyboardButton(f"{task[0]} {'✅' if task[1] == 'TRUE' else '❌'}", callback_data=str(i))]
        for i, task in enumerate(get_tasks())
    ]
    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(new_keyboard))
    
    if all_tasks_done():
        context.bot.send_message(chat_id=update.effective_chat.id, text="Уборка закончена. Спасибо!")
        ask_for_photo(update.effective_chat.id, context, photo_zones[0])
    
    update_all_chats(context)

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

    current_date = get_date_from_sheet()
    if current_date:
        bot2.send_message(chat_id=CHAT_ID, text=f"Смена за {current_date} завершена.")
    else:
        bot2.send_message(chat_id=CHAT_ID, text="Смена завершена.")

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

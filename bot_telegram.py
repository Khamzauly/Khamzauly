from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import os

json_str = os.getenv("LINK")
{"web":{"client_id":"73898426089-3lfiu34v8g4o3lda3r51qonm6mj0hpnr.apps.googleusercontent.com","project_id":"nudu-398911","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"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"}}


scopes = ['https://www.googleapis.com/auth/spreadsheets']
google_credentials = json.loads(json_str)
credentials = Credentials.from_service_account_info(google_credentials, scopes=scopes)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

# Функция для получения задач
def get_tasks():
    result = sheet.values().get(spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w", range="13.09.23!A2:D10").execute()
    return result.get('values', [])

# Функция для обновления задач
def update_task(row, user_name):
    sheet.values().update(
        spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w",
        range=f"13.09.23!B{row}:D{row}",
        body={"values": [[True, user_name, str(datetime.now())]]},
        valueInputOption="RAW"
    ).execute()

# Обработчик команды /start
def start(update: Update, context: CallbackContext):
    keyboard = []
    tasks = get_tasks()
    for i, task in enumerate(tasks):
        status = "✅" if task[1] == "TRUE" else "❌"
        keyboard.append([InlineKeyboardButton(f"{task[0]} {status}", callback_data=str(i))])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите задачу:', reply_markup=reply_markup)

# Обработчик кнопок
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    task_index = int(query.data)
    tasks = get_tasks()
    user_name = update.effective_user.first_name
    
    # Обновление данных в Google Sheets
    update_task(task_index + 2, user_name)
    
    # Здесь отправьте обновленный список задач всем пользователям

TOKEN = os.getenv("TOKEN")
# Основной код
updater = Updater(TOKEN)

dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()

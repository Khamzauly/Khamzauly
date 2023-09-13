from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime

# Инициализация Google Sheets API
json_file_path = '/client_secret_73898426089-3lfiu34v8g4o3lda3r51qonm6mj0hpnr.apps.googleusercontent.com.json'
scopes = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file(json_file_path, scopes=scopes)
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

# Основной код
updater = Updater("6655324353:AAEWkQb0b971nP4kf6OvS5s6fof0-NNfKHA")

dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()

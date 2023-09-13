import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Настройка Google Sheets API
scopes = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file('client_secret_73898426089-3lfiu34v8g4o3lda3r51qonm6mj0hpnr.apps.googleusercontent.com.json', scopes=scopes)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

# Получение данных из Google Sheets
def get_tasks():
    today = datetime.datetime.now().strftime("%d.%m.%y")
    range_name = f'{today}!A2:D'
    result = sheet.values().get(spreadsheetId="YOUR_SPREADSHEET_ID", range=range_name).execute()
    return result.get('values', [])

# Обновление данных в Google Sheets
def update_task(row, user_name):
    today = datetime.datetime.now().strftime("%d.%m.%y")
    range_name = f'{today}!B{row}:D{row}'
    values = [
        ["TRUE", user_name, datetime.datetime.now().strftime("%H:%M:%S")]
    ]
    body = {'values': values}
    sheet.values().update(spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w", range=range_name, valueInputOption="RAW", body=body).execute()

# Обработчик команды /start
def start(update: Update, context: CallbackContext):
    keyboard = []
    tasks = get_tasks()
    for i, task in enumerate(tasks):
        status = '✅' if task[1] == "TRUE" else ''
        name = task[2] if len(task) > 2 else ''
        keyboard.append([InlineKeyboardButton(f"{task[0]} {status} {name}", callback_data=str(i))])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите задачу:', reply_markup=reply_markup)

# Обработчик кнопок
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    task_index = int(query.data)
    user_name = update.effective_user.first_name
    
    # Обновление данных в Google Sheets
    update_task(task_index + 2, user_name)  # task_index + 2, потому что нумерация строк в Google Sheets начинается с 1, и у нас есть заголовок.
    
    # Здесь отправьте обновленный список задач всем пользователям

# Основной код
updater = Updater("6655324353:AAEWkQb0b971nP4kf6OvS5s6fof0-NNfKHA")
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()

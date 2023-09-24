from current_time import get_current_date_in_gmt6
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import json

# Инициализируем Google Sheets API
def initialize_service(json_str, scopes):
    google_credentials = json.loads(json_str)
    credentials = Credentials.from_service_account_info(google_credentials, scopes=scopes)
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    return sheet

def get_date_from_sheet(sheet):
    result = sheet.values().get(spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w", range="temp_evening!B2").execute()
    values = result.get('values', [])
    if len(values) > 0 and len(values[0]) > 0:
        return values[0][0]
    return None

def get_tasks(sheet):
    result = sheet.values().get(spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w", range="temp_evening!A4:B100").execute()
    return result.get('values', [])

def update_task(sheet, row, user_name):
    sheet.values().update(
        spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w",
        range=f"temp_evening!B{row}:D{row}",
        body={"values": [[True, user_name, str(get_current_date_in_gmt6())]]},
        valueInputOption="RAW"
    ).execute()

def all_tasks_done(sheet):
    tasks = get_tasks(sheet)
    return all(len(task) >= 2 and task[1] == "TRUE" for task in tasks)

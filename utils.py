# utils.py

from googleapiclient.discovery import build

chat_names = {}
shift_status = {}

def load_chat_names(sheet):
    global chat_names
    chat_names = {}
    result = sheet.values().get(spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w", range="чаты!A:B").execute()
    values = result.get('values', [])
    chat_names = {str(row[1]): str(row[0]) for row in values if len(row) > 1}

def load_shift_status(sheet):
    global shift_status
    result = sheet.values().get(spreadsheetId="1xjphW6Zlc3Hx73h2pTmFgDLeR4-MhVw2xITgjIOLN4w", range="чаты!A:C").execute()
    values = result.get('values', [])
    shift_status = {str(row[1]): str(row[2]) for row in values if len(row) > 2}

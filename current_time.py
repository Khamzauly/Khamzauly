from datetime import datetime, timedelta
import pytz

def get_current_datetime_in_gmt6():
    gmt6 = pytz.timezone('Asia/Almaty')  # GMT+6
    current_datetime = datetime.now(gmt6)
    # Перенос времени на 3 часа вперед
    return current_datetime

def get_current_date_in_gmt6():
    current_datetime = get_current_datetime_in_gmt6()
    return current_datetime.strftime('%Y-%m-%d %H:%M:%S')

def get_current_year():
    current_datetime = get_current_datetime_in_gmt6()
    return current_datetime.year

def get_last_year():
    current_datetime = get_current_datetime_in_gmt6()
    return current_datetime.year - 1

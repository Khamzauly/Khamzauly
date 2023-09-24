import os
from telegram.ext import Updater
from handlers import start_handler, button_handler, photo_handler

def main():
    TOKEN = os.getenv("TOKEN")
    updater = Updater(TOKEN)
    dp: Dispatcher = updater.dispatcher  # Здесь dp определен

    # Добавляем обработчики
    dp.add_handler(start_handler)
    dp.add_handler(button_handler)
    dp.add_handler(photo_handler)

    updater.start_polling()
    updater.idle()
    
if __name__ == '__main__':
    main()

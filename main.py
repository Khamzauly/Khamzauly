from telegram.ext import Updater
from handlers import start_handler, button_handler, photo_handler

TOKEN = os.getenv("TOKEN")

if __name__ == '__main__':
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # Добавляем обработчики
    dp.add_handler(start_handler)
    dp.add_handler(button_handler)
    dp.add_handler(photo_handler)

    updater.start_polling()
    updater.idle()

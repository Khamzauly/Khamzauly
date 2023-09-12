from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

TOKEN = os.getenv("TOKEN")

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    name = Column(String, primary_key=True)
    status = Column(String)
    worker = Column(String)

# Initialize DB
engine = create_engine('mysql+mysqlconnector://kespekz_Khamzauly:your_password@srv-pleskdb22.ps.kz:3306/kespekz_nuduregulator')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def start(update: Update, _: CallbackContext) -> None:
    tasks = session.query(Task).all()
    keyboard = [[InlineKeyboardButton(f"{task.name} {'✅' if task.status == 'Done' else ''}", callback_data=task.name)] for task in tasks]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose a task:", reply_markup=reply_markup)

def button(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    task_name = query.data

    task = session.query(Task).filter_by(name=task_name).first()
    if task:
        task.status = "Done"
        task.worker = query.from_user.username or query.from_user.first_name
        session.commit()

    tasks = session.query(Task).all()
    keyboard = [[InlineKeyboardButton(f"{task.name} {'✅' if task.status == 'Done' else ''} {task.worker if task.worker else ''}", callback_data=task.name)] for task in tasks]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text("Choose a task:", reply_markup=reply_markup)

updater = Updater(TOKEN)

updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()

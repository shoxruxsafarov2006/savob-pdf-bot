import telebot
import os
from flask import Flask
from threading import Thread

# 1. TOKEN ni o'rnating
TOKEN = "8923674018:AAFVp9TIGFLgmNj5hgY3UbLSCLAxg04L5Ss"
bot = telebot.TeleBot(TOKEN)

# 2. Flask serverini sozlash (bepul ishlashi uchun)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    # Render 10000 portini talab qiladi
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 3. Botingizning buyruqlari
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Bot ishga tushdi.")

# 4. Asosiy qism
if __name__ == "__main__":
    # Serverni ishga tushiramiz
    keep_alive()
    # Botingizni ishga tushiramiz
    print("Bot va server ishga tushdi...")
    bot.polling(none_stop=True)

import telebot
import os
from flask import Flask
from threading import Thread
from fpdf import FPDF

TOKEN = "8923674018:AAFVp9TIGFLgmNj5hgy3UbLSCLAXg04L5Ss"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

def create_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=text)
    pdf.output(filename)
    return filename

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Men PDF yaratuvchi botman. Menga matn yuboring, men uni PDF qilib beraman.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text
    file_name = f"{message.chat.id}.pdf"
    
    create_pdf(user_text, file_name)
    
    with open(file_name, "rb") as doc:
        bot.send_document(message.chat.id, doc)
    
    os.remove(file_name)

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)

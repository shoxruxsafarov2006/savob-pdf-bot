import telebot
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread
from fpdf import FPDF

# 1. API va Token sozlamalari (Bularni o'zingizniki bilan almashtiring)
genai.configure(api_key="AQ.Ab8RN6JExLw1QCatlmSjQ9rahzUtHEUo1NhFFQsRFyisxrY_xQ")
bot = telebot.TeleBot("8923674018:AAGq00YUBiTmpKjPKbQ7twP6JxHM0yvBPL4")

# Flask (Render uchun)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot ishlayapti!"
def run(): app.run(host='0.0.0.0', port=10000)
Thread(target=run).start()

# AI orqali savol generatsiya
def generate_content(topic, count):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"{topic} mavzusida {count} ta savol va javob tuzib ber.")
    return response.text

# PDF yaratish
def create_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=text)
    pdf.output(filename)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Mavzuni va savollar sonini yozing. Masalan: 'Psixologiya 5'")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        parts = message.text.split()
        topic = parts[0]
        count = parts[1] if len(parts) > 1 else "5"
        bot.send_message(message.chat.id, "Kuting, AI savollarni tuzmoqda...")
        text = generate_content(topic, count)
        file_name = f"{message.chat.id}.pdf"
        create_pdf(text, file_name)
        with open(file_name, "rb") as doc:
            bot.send_document(message.chat.id, doc)
        os.remove(file_name)
    except Exception as e:
        bot.reply_to(message, "Xatolik yuz berdi!")

if __name__ == "__main__":
    bot.polling(none_stop=True)

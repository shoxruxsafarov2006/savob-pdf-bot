import telebot
from telebot import types
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread
from fpdf import FPDF
from PIL import Image

# Sozlamalar
API_KEY = "AIzaSyD-..." # O'zingizning haqiqiy Google API kalitingizni yozing
BOT_TOKEN = "8923674018:AAGq00YUBiTmpKjPKbQ7twP6JxHM0yvBPL4"

genai.configure(api_key=API_KEY)
bot = telebot.TeleBot(BOT_TOKEN)

# Flask (Render uchun)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot ishlayapti!"
def run(): app.run(host='0.0.0.0', port=10000)
Thread(target=run).start()

user_data = {}

# --- Yordamchi Funksiyalar ---
def generate_content(topic, mode):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"{topic} mavzusi bo'yicha {mode} uchun professional ma'lumotlarni jadval ko'rinishida (Atama | Ta'rif) formatida ber."
    response = model.generate_content(prompt)
    return response.text

# --- Bot Mantiqi ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Xush kelibsiz! Tilni tanlang:", reply_markup=types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz")))

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_lang(call):
    user_data[call.message.chat.id] = {"lang": "uz"}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Taqdimot", "Slayd", "Krossvord", "Glossariy")
    bot.send_message(call.message.chat.id, "Kerakli rejimni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Taqdimot", "Slayd", "Krossvord", "Glossariy"])
def set_mode(message):
    user_data[message.chat.id]["mode"] = message.text
    user_data[message.chat.id]["step"] = "topic"
    bot.send_message(message.chat.id, "Mavzuni yozing:")

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get("step") == "topic")
def set_topic(message):
    user_data[message.chat.id]["topic"] = message.text
    user_data[message.chat.id]["step"] = "wait_for_photo"
    bot.send_message(message.chat.id, "PDF uchun fon rasmini yuboring:")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    if user_data.get(chat_id, {}).get("step") == "wait_for_photo":
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        bg_path = f"bg_{chat_id}.jpg"
        with open(bg_path, 'wb') as f: f.write(downloaded)
        user_data[chat_id]["bg"] = bg_path
        create_pdf(chat_id)

def create_pdf(chat_id):
    data = user_data[chat_id]
    msg = bot.send_message(chat_id, "⏳ PDF tayyorlanmoqda...")
    
    content = generate_content(data["topic"], data["mode"])
    
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(data["bg"]):
        pdf.image(data["bg"], 0, 0, 210, 297)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, data["topic"], ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=11)
    for line in content.split('\n'):
        if "|" in line:
            parts = line.split('|')
            pdf.cell(50, 10, parts[0][:25], 1)
            pdf.multi_cell(140, 10, parts[1][:70], 1)
            
    file_name = f"{chat_id}.pdf"
    pdf.output(file_name)
    
    with open(file_name, "rb") as f: bot.send_document(chat_id, f)
    
    os.remove(file_name)
    os.remove(data["bg"])
    del user_data[chat_id]
    bot.send_message(chat_id, "✅ Tayyor!")

if __name__ == "__main__":
    bot.polling(none_stop=True)

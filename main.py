import telebot
from telebot import types
import os
import time
import google.generativeai as genai
from flask import Flask
from threading import Thread
from fpdf import FPDF

# Sozlamalar
API_KEY = "AQ.Ab8RN6JExLw1QCatlmSjQ9rahzUtHEUo1NhFFQsRFyisxrY_xQ"
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

# --- Yordamchi menyular ---
def get_lang_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"))
    markup.add(types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"))
    markup.add(types.InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"))
    return markup

def get_main_menu(lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btns = {
        "uz": ["1. Taqdimot", "2. Slayd", "3. Krossvord", "4. Glossariy", "5. Tilni o'zgartirish"],
        "ru": ["1. Презентация", "2. Слайд", "3. Кроссворд", "4. Глоссарий", "5. Сменить язык"],
        "en": ["1. Presentation", "2. Slide", "3. Crossword", "4. Glossary", "5. Change Language"]
    }
    labels = btns.get(lang, btns["uz"])
    markup.add(labels[0], labels[1]); markup.add(labels[2], labels[3]); markup.add(labels[4])
    return markup

def get_design_menu():
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(*[types.InlineKeyboardButton(f"Dizayn {i}", callback_data=f"design_{i}") for i in range(1, 16)])
    return markup

# --- Bot mantiqi ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bizni tanlaganingizdan xursandmiz! Tilni tanlang:", reply_markup=get_lang_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_lang(call):
    lang = call.data.split("_")[1]
    user_data[call.message.chat.id] = {"lang": lang}
    bot.edit_message_text("Kerakli menyuni tanlang:", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu(lang))

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return start(message)
    
    if "5." in message.text: return start(message)
    
    if "mode" not in user_data[chat_id]:
        user_data[chat_id]["mode"] = message.text
        bot.send_message(chat_id, "Mavzuni yozing:")
    elif "topic" not in user_data[chat_id]:
        user_data[chat_id]["topic"] = message.text
        bot.send_message(chat_id, "Dizaynni tanlang:", reply_markup=get_design_menu())
    elif "pages" not in user_data[chat_id]:
        try:
            pages = int(message.text)
            if 5 <= pages <= 40:
                user_data[chat_id]["pages"] = pages
                generate_document(chat_id)
            else: bot.send_message(chat_id, "5-40 oralig'ida raqam kiriting!")
        except: bot.send_message(chat_id, "Faqat raqam kiriting!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("design_"))
def set_design(call):
    user_data[call.message.chat.id]["design"] = call.data.split("_")[1]
    bot.send_message(call.message.chat.id, "Varaqlar sonini kiriting (5-40):")

def generate_document(chat_id):
    msg = bot.send_message(chat_id, "⏳ Tayyorlanmoqda... 0%")
    for i in range(1, 6):
        time.sleep(1)
        bot.edit_message_text(f"⏳ Tayyorlanmoqda... {i*20}%", chat_id, msg.message_id)
    
    # AI qismi va PDF yaratish
    file_name = f"{chat_id}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Mavzu: {user_data[chat_id]['topic']} (Rejim: {user_data[chat_id]['mode']})", ln=True, align='C')
    pdf.output(file_name)
    
    with open(file_name, "rb") as doc: bot.send_document(chat_id, doc)
    os.remove(file_name)
    bot.send_message(chat_id, "✅ Hammasi tayyor! Bizning xizmat sizga ma'qul tushdi deb umid qilamiz. 🌟")
    del user_data[chat_id]

if __name__ == "__main__":
    bot.polling(none_stop=True)

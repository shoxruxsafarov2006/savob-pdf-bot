import telebot
from telebot import types
import os
import time
import google.generativeai as genai
from flask import Flask
from threading import Thread
from fpdf import FPDF
from PIL import Image

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

# --- Menyu funksiyalari ---
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

# --- Bot mantiqi ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bizni tanlaganingizdan xursandmiz! Tilni tanlang:", reply_markup=get_lang_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_lang(call):
    lang = call.data.split("_")[1]
    user_data[call.message.chat.id] = {"lang": lang}
    bot.edit_message_text("Tanlandi! Kerakli menyuni tanlang:", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu(lang))

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    if chat_id in user_data and user_data[chat_id].get("step") == "wait_for_photo":
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        bg_path = f"bg_{chat_id}.jpg"
        with open(bg_path, 'wb') as new_file: new_file.write(downloaded_file)
        user_data[chat_id]["bg"] = bg_path
        user_data[chat_id]["step"] = "pages"
        bot.send_message(chat_id, "Fon qabul qilindi! Endi necha varaq bo'lishini yozing (5-40):")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return start(message)
    if "5." in message.text or message.text == "/start": return start(message)
    
    if "mode" not in user_data[chat_id]:
        user_data[chat_id]["mode"] = message.text
        user_data[chat_id]["step"] = "topic"
        bot.send_message(chat_id, "Endi qaysi mavzuda tayyorlash kerakligini yozing:")
    elif user_data[chat_id].get("step") == "topic":
        user_data[chat_id]["topic"] = message.text
        user_data[chat_id]["step"] = "wait_for_photo"
        bot.send_message(chat_id, "Yaxshi! Endi PDF uchun fon rasmini yuboring:")
    elif user_data[chat_id].get("step") == "pages":
        try:
            pages = int(message.text)
            if 5 <= pages <= 40:
                user_data[chat_id]["pages"] = pages
                generate_document(chat_id)
            else: bot.send_message(chat_id, "5 dan 40 gacha son kiriting!")
        except: bot.send_message(chat_id, "Iltimos, raqam formatida kiriting!")

def generate_document(chat_id):
    msg = bot.send_message(chat_id, "⏳ PDF tayyorlanmoqda... 0%")
    for i in range(1, 6):
        time.sleep(1)
        bot.edit_message_text(f"⏳ PDF tayyorlanmoqda... {i*20}%", chat_id, msg.message_id)
    
    data = user_data[chat_id]
    pdf = FPDF()
    pdf.add_page()
    if "bg" in data:
        pdf.image(data["bg"], x=0, y=0, w=210, h=297)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Mavzu: {data['topic']}", ln=True, align='C')
    
    file_name = f"{chat_id}.pdf"
    pdf.output(file_name)
    
    with open(file_name, "rb") as doc: bot.send_document(chat_id, doc)
    os.remove(file_name)
    if "bg" in data and os.path.exists(data["bg"]): os.remove(data["bg"])
    
    bot.send_message(chat_id, "✅ Hammasi tayyor! Bizning xizmat sizga ma'qul tushdi deb umid qilamiz. 🌟")
    del user_data[chat_id]

if __name__ == "__main__":
    bot.polling(none_stop=True)

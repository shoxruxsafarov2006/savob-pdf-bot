import telebot
from telebot import types
import os
import google.generativeai as genai
from flask import Flask, request
from fpdf import FPDF

API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

genai.configure(api_key=API_KEY)
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

user_data = {}

# Turli tillar uchun menyu va matnlar
TEXTS = {
    "uz": {"choose": "Kerakli rejimni tanlang:", "modes": ["Taqdimot", "Slayd", "Krossvord", "Glossariy"], "topic": "Mavzuni yozing:", "wait": "PDF uchun fon rasmini yuboring:", "wait_pdf": "⏳ PDF tayyorlanmoqda..."},
    "ru": {"choose": "Выберите нужный режим:", "modes": ["Презентация", "Слайд", "Кроссворд", "Глоссарий"], "topic": "Напишите тему:", "wait": "Отправьте фоновое изображение для PDF:", "wait_pdf": "⏳ PDF готовится..."},
    "en": {"choose": "Choose the mode:", "modes": ["Presentation", "Slide", "Crossword", "Glossary"], "topic": "Enter the topic:", "wait": "Send a background image for PDF:", "wait_pdf": "⏳ PDF is being prepared..."}
}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"))
    markup.add(types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"))
    markup.add(types.InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"))
    bot.send_message(message.chat.id, "Tilni tanlang / Выберите язык / Select language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_lang(call):
    lang = call.data.split("_")[1]
    user_data[call.message.chat.id] = {"lang": lang}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for mode in TEXTS[lang]["modes"]: markup.add(mode)
    bot.send_message(call.message.chat.id, TEXTS[lang]["choose"], reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    
    data = user_data[chat_id]
    lang = data.get("lang", "uz")
    
    # Rejimni tanlash
    if message.text in TEXTS[lang]["modes"]:
        data["mode"] = message.text
        data["step"] = "topic"
        bot.send_message(chat_id, TEXTS[lang]["topic"])
    # Mavzuni qabul qilish
    elif data.get("step") == "topic":
        data["topic"] = message.text
        data["step"] = "wait_for_photo"
        bot.send_message(chat_id, TEXTS[lang]["wait"])

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    if user_data.get(chat_id, {}).get("step") == "wait_for_photo":
        # ... (rasm yuklash va PDF yaratish qismi avvalgidek qoladi)
        # Eslatma: generate_content funksiyasida 'lang' o'zgaruvchisini ishlatib,
        # promptni o'sha tilda so'rashni unutmang.
        bot.send_message(chat_id, TEXTS[user_data[chat_id]["lang"]]["wait_pdf"])
        # create_pdf(chat_id) chaqiring

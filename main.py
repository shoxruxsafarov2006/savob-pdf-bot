import telebot
from telebot import types
import os
import time
import google.generativeai as genai
from flask import Flask, request
from fpdf import FPDF

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))
genai.configure(api_key=os.getenv("API_KEY"))
app = Flask(__name__)

user_data = {}

# Tillarga mos matnlar
TEXTS = {
    "uz": {"welcome": "Bizni tanlaganingizdan xursandmiz!", "lang": "Tilni tanlang:", "modes": ["Taqdimot", "Slayd", "Krossvord", "Glossariy", "Tilni o'zgartirish"], "topic": "Mavzuni yozing:", "pages": "Necha varaq bo'lsin? (5-40):", "wait": "⏳ PDF tayyorlanmoqda, kutish vaqti: 15 soniya..."},
    "ru": {"welcome": "Мы рады, что вы выбрали нас!", "lang": "Выберите язык:", "modes": ["Презентация", "Слайд", "Кроссворд", "Глоссарий", "Сменить язык"], "topic": "Напишите тему:", "pages": "Сколько страниц? (5-40):", "wait": "⏳ PDF готовится, ожидание: 15 секунд..."},
    "en": {"welcome": "We are glad you chose us!", "lang": "Select language:", "modes": ["Presentation", "Slide", "Crossword", "Glossary", "Change language"], "topic": "Enter the topic:", "pages": "How many pages? (5-40):", "wait": "⏳ PDF is preparing, wait: 15 seconds..."}
}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bizni tanlaganingizdan xursandmiz! / Мы рады что вы выбрали нас! / We are glad you chose us!")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
               types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
               types.InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"))
    bot.send_message(message.chat.id, "Tilni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_lang(call):
    lang = call.data.split("_")[1]
    user_data[call.message.chat.id] = {"lang": lang}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for mode in TEXTS[lang]["modes"]: markup.add(mode)
    bot.send_message(call.message.chat.id, TEXTS[lang]["lang"], reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return start(message)
    lang = user_data[chat_id]["lang"]
    
    if message.text == TEXTS[lang]["modes"][4]: return start(message)
    if message.text in TEXTS[lang]["modes"]:
        user_data[chat_id].update({"mode": message.text, "step": "topic"})
        bot.send_message(chat_id, TEXTS[lang]["topic"])
    elif user_data[chat_id].get("step") == "topic":
        user_data[chat_id].update({"topic": message.text, "step": "pages"})
        bot.send_message(chat_id, TEXTS[lang]["pages"])
    elif user_data[chat_id].get("step") == "pages":
        pages = int(message.text) if message.text.isdigit() else 5
        user_data[chat_id].update({"pages": max(5, min(40, pages)), "step": "photo"})
        bot.send_message(chat_id, "Fon uchun rasm yuboring:")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    if user_data.get(chat_id, {}).get("step") == "photo":
        lang = user_data[chat_id]["lang"]
        bot.send_message(chat_id, TEXTS[lang]["wait"])
        time.sleep(15) # Timer simulyatsiyasi
        bot.send_message(chat_id, "✅ Tayyor! Xizmatimiz sizga ma'qul tushdi degan umiddamiz.")

@app.route(f'/{os.getenv("BOT_TOKEN")}', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

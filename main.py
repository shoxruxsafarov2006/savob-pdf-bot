import telebot
from telebot import types
from fpdf import FPDF
import os
from flask import Flask
import threading

# Koyeb bepul hostingda o'chib qolmasligi uchun kichik Web Server qo'shamiz
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

TOKEN = "8923674018:AAFVp9TIGFLgmNj5hgY3UbLSCLAxg04L5Ss"
bot = telebot.TeleBot(TOKEN)

# Pastki doimiy menyu tugmalarini yaratish
def bosh_menyu_tugmalari():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn1 = types.KeyboardButton("💼 Xizmatlar")
    btn2 = types.KeyboardButton("🌐 Tilni o'zgartirish")
    btn3 = types.KeyboardButton("🔐 Obuna")
    btn4 = types.KeyboardButton("🎁 Bepul foydalanish")
    btn5 = types.KeyboardButton("👤 Shaxsiy raqam")
    btn6 = types.KeyboardButton("🎬 Qo'llanma")
    
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

# /start buyrug'i
@bot.message_handler(commands=['start'])
def salom(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    btn_uz = types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz")
    btn_ru = types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
    btn_en = types.InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")
    
    markup.add(btn_uz, btn_ru, btn_en)
    
    start_text = (
        "🇺🇿 Tugmalar, va boshqaruv xabarlari tilini tanlash uchun quyidagi tugmalardan foydalaning.\n\n"
        "🇷🇺 Используйте следующие кнопки для выбора языка интерфейса.\n\n"
        "🇺🇸 Use the following buttons to select the interface language."
    )
    
    bot.send_message(message.chat.id, start_text, reply_markup=markup)

# Til tanlanganda
@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def til_tanlandi(call):
    chat_id = call.message.chat.id
    menyu = bosh_menyu_tugmalari()
    
    if call.data == "lang_uz":
        bot.answer_callback_query(call.id, "O'zbek tili tanlandi!")
        bot.send_message(chat_id, "🇺🇿 O'zbek tili faollashtirildi.\n\nQuyidagi menyudan foydalaning:", reply_markup=menyu)
    elif call.data == "lang_ru":
        bot.answer_callback_query(call.id, "Выбран русский язык!")
        bot.send_message(chat_id, "🇷🇺 Выбран русский язык.\n\nИспользуйте меню ниже:", reply_markup=menyu)
    elif call.data == "lang_en":
        bot.answer_callback_query(call.id, "English selected!")
        bot.send_message(chat_id, "🇺🇸 English language selected.\n\nUse the menu below:", reply_markup=menyu)

# Xabarlar va tugmalar bilan ishlash
@bot.message_handler(func=lambda message: True)
def xabarlarni_tutish(message):
    chat_id = message.chat.id
    text = message.text

    if text == "💼 Xizmatlar":
        bot.send_message(chat_id, "Siz 'Xizmatlar' bo'limini tanladingiz. Bu yerda sizga PDF yaratish xizmatini taklif qilamiz. Menga matn yuboring!")
    elif text == "🌐 Tilni o'zgartirish":
        salom(message)
    elif text == "🔐 Obuna":
        bot.send_message(chat_id, "Sizda sun'iy intellektdan foydalanishga ruxsat yo'q!\n\nObuna sotib oling yoki do'stlaringizni taklif qiling.")
    elif text == "🎁 Bepul foydalanish":
        bot.send_message(chat_id, "Do'stlaringizga botni ulashing va bepul urinishlarga ega bo'ling!")
    elif text == "👤 Shaxsiy raqam":
        bot.send_message(chat_id, f"Sizning shaxsiy ID raqamingiz: {chat_id}")
    elif text == "🎬 Qo'llanma":
        bot.send_message(chat_id, "Botdan foydalanish bo'yicha video-qo'llanma tez kunda joylanadi.")
    else:
        bot.send_message(chat_id, "Matningiz qabul qilindi. PDF fayl tayyorlanmoqda...")
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=14)
        pdf.cell(200, 10, text="Sizning PDF Hujjatingiz", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(10)
        pdf.multi_cell(0, 10, text=text)
        
        file_name = f"hujjat_{chat_id}.pdf"
        pdf.output(file_name)
        
        with open(file_name, 'rb') as file:
            bot.send_document(chat_id, file, caption="Mana, tayyor PDF! 📄")
            
        if os.path.exists(file_name):
            os.remove(file_name)

# Web serverni alohida oqimda (thread) ishga tushiramiz
threading.Thread(target=run_web_server, daemon=True).start()

print("Koyeb serverida bot ishga tushdi...")
bot.polling(non_stop=True)

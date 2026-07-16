import os
import logging
from fpdf import FPDF
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

# Sozlamalar
logging.basicConfig(level=logging.INFO)
genai.configure(api_key="AQ.Ab8RN6LD-JkobynJYdHRg2SqckdZdTjCxsqXI3Ia-ReXLEiA_A")
model = genai.GenerativeModel('gemini-1.5-flash')

# Bosqichlar
MENU, WAIT_TOPIC = range(2)

# PDF yaratish funksiyasi
def create_pdf(text, filename="slayd.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Matnni kodlash xatosiz yozish
    text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=text)
    pdf.output(filename)
    return filename

# Asosiy menyu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_keyboard = [
        ['Taqdimot', 'Glossary'],
        ['Slayd', 'Tilni oʻzgartirish']
    ]
    await update.message.reply_text(
        "Asosiy menyu:", 
        reply_markup=ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
    )
    return MENU

# Tanlovni qabul qilish
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == 'Tilni oʻzgartirish':
        return await start(update, context)
    
    context.user_data['type'] = text
    await update.message.reply_text(f"Siz '{text}' ni tanladingiz. Mavzuni yozing:")
    return WAIT_TOPIC

# PDF yaratish va yuborish
async def generate_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text
    await update.message.reply_text("Tayyorlanyapti, kuting...")
    
    try:
        response = model.generate_content(f"{topic} mavzusida {context.user_data['type']} uchun qisqa va aniq ma'lumot yoz.")
        filename = create_pdf(response.text)
        await update.message.reply_document(document=open(filename, 'rb'))
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text("Xatolik yuz berdi. Qayta urinib ko'ring.")
    
    return await start(update, context)

if __name__ == '__main__':
    app = ApplicationBuilder().token("8923674018:AAFVp9TIGFLgmNj5hgY3UbLSCLAxg04L5Ss").build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler)],
            WAIT_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_pdf)],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    
    app.add_handler(conv_handler)
    app.run_polling()

import os
import logging
from fpdf import FPDF
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Sozlamalar
logging.basicConfig(level=logging.INFO)
genai.configure(api_key="AQ.Ab8RN6LD-JkobynJYdHRg2SqckdZdTjCxsqXI3Ia-ReXLEiA_A")
model = genai.GenerativeModel('gemini-1.5-flash')

# PDF yaratish
def create_pdf(text, filename="slayd.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Matnni tozalash
    text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=text)
    pdf.output(filename)
    return filename

# Bot buyruqlari
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Mavzuni yozing, men sizga PDF shaklida slayd tayyorlab beraman:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text
    await update.message.reply_text("Tayyorlanyapti, kuting...")
    
    try:
        # AI dan qisqa javob olish
        response = model.generate_content(f"{topic} haqida qisqa va aniq 5 ta asosiy fikr yoz.")
        
        # PDF yaratish va yuborish
        filename = create_pdf(response.text)
        await update.message.reply_document(document=open(filename, 'rb'))
        
        # Faylni tozalash
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"Xatolik yuz berdi: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token("8923674018:AAFVp9TIGFLgmNj5hgY3UbLSCLAxg04L5Ss").build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# 1. AI sozlamasi
genai.configure(api_key="AQ.Ab8RN6LD-JkobynJYdHRg2SqckdZdTjCxsqXI3Ia-ReXLEiA_A")
model = genai.GenerativeModel('gemini-pro')

LANGUAGE, MAIN_MENU, SLIDE_NAME, SLIDE_COUNT = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Tilni tanlang:", reply_markup=ReplyKeyboardMarkup([['O\'zbekcha', 'English']], one_time_keyboard=True))
    return LANGUAGE

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu_keyboard = [['Slayd', 'Taqdimot'], ['Glossary', 'Tilni tanlash']]
    await update.message.reply_text("Asosiy menyu:", reply_markup=ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True))
    return MAIN_MENU

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == 'Tilni tanlash': return await start(update, context)
    context.user_data['type'] = update.message.text
    await update.message.reply_text("Mavzuni kiriting:")
    return SLIDE_NAME

async def slide_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['topic'] = update.message.text
    await update.message.reply_text("Necha varaq bo'lsin?")
    return SLIDE_COUNT

async def slide_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = context.user_data['topic']
    type_ = context.user_data['type']
    await update.message.reply_text("Sizga ma'lumot tayyorlayapman, biroz kuting...")
    response = model.generate_content(f"Mavzu: {topic}. Turi: {type_}. Iltimos, buni qisqa va tushunarli qilib yozib ber.")
    await update.message.reply_text(response.text)
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token("8923674018:AAFVp9TIGFLgmNj5hgY3UbLSCLAxg04L5Ss").build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_language)],
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)],
            SLIDE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, slide_name)],
            SLIDE_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, slide_count)],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    app.add_handler(conv_handler)
    app.run_polling()

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Bosqichlar
LANGUAGE, MAIN_MENU, SLIDE_NAME, SLIDE_COUNT = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men sizga bu bot ma'qul tushadi. Iltimos, tilni tanlang:",
        reply_markup=ReplyKeyboardMarkup([['O\'zbekcha', 'English']], one_time_keyboard=True)
    )
    return LANGUAGE

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Siz so'ragan 4 ta tugma
    menu_keyboard = [['Slayd', 'Taqdimot'], ['Glossary', 'Tilni tanlash']]
    await update.message.reply_text(
        "Asosiy menyu:",
        reply_markup=ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
    )
    return MAIN_MENU

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == 'Tilni tanlash':
        return await start(update, context)
    else:
        # Slayd, Taqdimot yoki Glossary tanlansa
        await update.message.reply_text(f"Siz {text} ni tanladingiz. Slayd nomini kiriting:")
        return SLIDE_NAME

async def slide_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['slide_name'] = update.message.text
    await update.message.reply_text("Slayd necha varaqdan iborat bo'lsin?")
    return SLIDE_COUNT

async def slide_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Slaydingiz mukammal darajada tayyorlanmoqda, kuting...")
    await update.message.reply_text("Bizni tanlaganingizdan xursandmiz! ❤️")
    return ConversationHandler.END

if __name__ == '__main__':
    # Tokeningizni tekshirib oling!
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

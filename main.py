from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Bosqichlar
LANGUAGE, MENU, SLIDE_NAME, SLIDE_COUNT = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Men sizga bu bot maqul tushadi. Iltimos, tilni tanlang:",
        reply_markup=ReplyKeyboardMarkup([['O\'zbekcha', 'English']], one_time_keyboard=True))
    return LANGUAGE

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Tilni saqlab qolish
    await update.message.reply_text("Yaxshi! Xizmatni tanlang:",
        reply_markup=ReplyKeyboardMarkup([['1. Glossary', '2. Taqdimot', '3. Slayd']], one_time_keyboard=True))
    return MENU

async def menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if '3. Slayd' in choice:
        await update.message.reply_text("Slayd nomini kiriting:")
        return SLIDE_NAME
    # Boshqa variantlar uchun...
    return MENU

async def slide_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['slide_name'] = update.message.text
    await update.message.reply_text("Slayd necha varaqdan iborat bo'lsin?")
    return SLIDE_COUNT

async def slide_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Bu yerda AI yordamida slayd yaratish funksiyasini chaqiramiz
    await update.message.reply_text("Slaydingiz tayyorlanmoqda, kuting...")
    # Slayd tayyor bo'lgach:
    await update.message.reply_text("Bizni tanlaganingizdan xursandmiz! ❤️")
    return ConversationHandler.END

# ConversationHandler ni shu yerda sozlaymiz


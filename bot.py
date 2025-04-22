
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

TOKEN = "YOUR_BOT_TOKEN_HERE"

menu_keyboard = ReplyKeyboardMarkup(
    [['💐 Каталог', '🛍 Заказать'], ['📞 Контакты']],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать в Flora Пермь! Выберите действие:", reply_markup=menu_keyboard
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '💐 Каталог':
        await update.message.reply_text("Вот наш каталог:
🌹 Букет 1
🌷 Букет 2
🌻 Букет 3")
    elif text == '🛍 Заказать':
        await update.message.reply_text("Для заказа напишите: имя и номер телефона")
    elif text == '📞 Контакты':
        await update.message.reply_text("📍 Пермь, Цветочная 12
📞 +7 (342) 123-45-67
⏰ 9:00–21:00")
    else:
        await update.message.reply_text("Я пока не понимаю эту команду 😊")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()

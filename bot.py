
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

# Вставь сюда свой токен
TOKEN = "7973085918:AAGgI8K0wMWVKspRad0y53EKbirCCjijqXE"

# Главное меню
main_menu = ReplyKeyboardMarkup(
    [['💐 Каталог', '🛍 Заказать'], ['📞 Контакты']],
    resize_keyboard=True
)

# Кнопки каталога
catalog_menu = ReplyKeyboardMarkup(
    [['🌹 Букет 1'], ['🌷 Букет 2'], ['🌻 Букет 3'], ['⬅️ Назад']],
    resize_keyboard=True
)

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать в Flora Пермь! Выберите действие:",
        reply_markup=main_menu
    )

# Обработка команд
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '💐 Каталог':
        await update.message.reply_text("Выберите букет:", reply_markup=catalog_menu)

    elif text == '🌹 Букет 1':
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Заказать 🌹", callback_data="order_1")]])
        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/0d3/nkr6256qhf6b79bdh86ezgl9kufycbei.jpeg",
            caption="🌹 Букет 1 — 18230₽",
            reply_markup=keyboard
        )

    elif text == '🌷 Букет 2':
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Заказать 🌷", callback_data="order_2")]])
        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/0fc/abo9003vbqn2fusdjosgknhsxwczpq7j.jpeg",
            caption="🌷 Букет 2 — 18230₽",
            reply_markup=keyboard
        )

    elif text == '🌻 Букет 3':
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Заказать 🌻", callback_data="order_3")]])
        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/e25/f2bvr479poaj4h1qp9fx6o41slldkwqt.jpg",
            caption="🌻 Букет 3 — 32600₽",
            reply_markup=keyboard
        )

    elif text == '⬅️ Назад':
        await update.message.reply_text("Вы вернулись в главное меню", reply_markup=main_menu)

    elif text == '🛍 Заказать':
        await update.message.reply_text("Для заказа напишите: имя и номер телефона")

    elif text == '📞 Контакты':
        await update.message.reply_text(
            "📍 Пермь, Карпинского 91д\n📞 +7 (342) 214-88-99\n⏰ 9:00–21:00"
        )

    else:
        await update.message.reply_text("Я пока не понимаю эту команду 😊")

# Обработка нажатий на кнопки "Заказать"
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    bouquet = query.data.split("_")[1]
    names = {"1": "🌹 Букет 1", "2": "🌷 Букет 2", "3": "🌻 Букет 3"}
    name = names.get(bouquet, "Букет")

    await query.message.reply_text(
        f"Вы выбрали {name}. Пожалуйста, отправьте ваше имя и номер телефона для оформления заказа:"
    )

# Запуск бота
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()

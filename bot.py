
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

# Токен
TOKEN = os.environ.get("BOT_TOKEN")

# Доступность букетов
bouquet_availability = {
    "1": False,  # Букет 1 временно недоступен
    "2": True,
    "3": True
}

# Главное меню
main_menu = ReplyKeyboardMarkup(
    [['💐 Каталог', '🛍 Заказать'], ['📞 Контакты']],
    resize_keyboard=True
)

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать в Flora Пермь! Выберите действие:",
        reply_markup=main_menu
    )

# Каталог меню — строим динамически
def get_catalog_menu():
    buttons = []
    if bouquet_availability["1"]:
        buttons.append(['🌹 Букет 1'])
    else:
        buttons.append(['🌹 Букет 1 (нет в наличии)'])
    if bouquet_availability["2"]:
        buttons.append(['🌷 Букет 2'])
    if bouquet_availability["3"]:
        buttons.append(['🌻 Букет 3'])
    buttons.append(['⬅️ Назад'])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# Обработка текстовых сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == '💐 Каталог':
        await update.message.reply_text("Выберите букет:", reply_markup=get_catalog_menu())

    elif text.startswith('🌹 Букет 1'):
        if bouquet_availability["1"]:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Заказать 🌹", callback_data="order_1")]])
            caption = "🌹 Букет 1 — 18230₽"
        else:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Нет в наличии", callback_data="unavailable")]])
            caption = "🌹 Букет 1 — 18230₽\n\n❌ Временно нет в наличии"

        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/0d3/nkr6256qhf6b79bdh86ezgl9kufycbei.jpeg",
            caption=caption,
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

# Обработка кнопок
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("order_"):
        bouquet = query.data.split("_")[1]
        names = {"1": "🌹 Букет 1", "2": "🌷 Букет 2", "3": "🌻 Букет 3"}
        name = names.get(bouquet, "Букет")

        if not bouquet_availability[bouquet]:
            await query.message.reply_text("Извините, этот букет сейчас недоступен.")
            return

        await query.message.reply_text(
            f"Вы выбрали {name}. Пожалуйста, отправьте ваше имя и номер телефона для оформления заказа:"
        )

    elif query.data == "unavailable":
        await query.message.reply_text("Извините, этот букет сейчас недоступен.")

# Запуск
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()

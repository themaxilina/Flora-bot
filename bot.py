
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

main_menu = ReplyKeyboardMarkup(
    [['💐 Каталог', '🛍 Заказать'], ['📞 Контакты']],
    resize_keyboard=True
)

catalog_menu = ReplyKeyboardMarkup(
    [['🌹 Букет 1'], ['🌷 Букет 2'], ['🌻 Букет 3'], ['⬅️ Назад']],
    resize_keyboard=True
)

# Остатки букетов
stock = {
    "1": 0,  # нет в наличии
    "2": 5,
    "3": 3
}

# Временное хранилище для состояний пользователей
user_state = {}

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать в Flora Пермь! Выберите действие:",
        reply_markup=main_menu
    )

# Обработка каталога
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if text == '💐 Каталог':
        await update.message.reply_text("Выберите букет:", reply_markup=catalog_menu)

    elif text.startswith('🌹 Букет 1'):
        if stock["1"] <= 0:
            await update.message.reply_photo(
                photo="https://floraservis.ru/upload/iblock/0d3/nkr6256qhf6b79bdh86ezgl9kufycbei.jpeg",
                caption="🌹 Букет 1 — ❌ Нет в наличии"
            )
        else:
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

    elif text == '📞 Контакты':
        await update.message.reply_text(
            "📍 Пермь, Карпинского 91д\n📞 +7 (342) 214-88-99\n⏰ 9:00–21:00"
        )

# Обработка кнопки "Заказать"
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    bouquet_id = query.data.split("_")[1]
    user_state[user_id] = {"bouquet_id": bouquet_id}

    # Шаг 1 — выбор даты
    date_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Сегодня", callback_data="date_today")],
        [InlineKeyboardButton("Завтра", callback_data="date_tomorrow")],
        [InlineKeyboardButton("Послезавтра", callback_data="date_after")]
    ])
    await query.message.reply_text("Выберите дату доставки:", reply_markup=date_keyboard)

# Обработка выбора даты и времени
async def handle_date_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("date_"):
        date_choice = data.split("_")[1]
        user_state[user_id]["date"] = date_choice

        # Шаг 2 — выбор времени
        time_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("09:00–12:00", callback_data="time_morning")],
            [InlineKeyboardButton("12:00–15:00", callback_data="time_day")],
            [InlineKeyboardButton("15:00–18:00", callback_data="time_evening")]
        ])
        await query.message.reply_text("Выберите время доставки:", reply_markup=time_keyboard)

    elif data.startswith("time_"):
        time_choice = data.split("_")[1]
        user_state[user_id]["time"] = time_choice

        # Шаг 3 — запрос имени и телефона
        await query.message.reply_text("Введите ваше имя и номер телефона (например: Анна, +79001234567)")

# Обработка текста: имя и телефон
async def collect_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id in user_state and "time" in user_state[user_id]:
        user_state[user_id]["contact"] = text

        info = user_state[user_id]
        await update.message.reply_text(
            f"Спасибо за заказ!\n\n"
            f"Букет №{info['bouquet_id']}\n"
            f"Дата: {info['date']}\n"
            f"Время: {info['time']}\n"
            f"Контакт: {info['contact']}"
        )

        # Уменьшаем количество
        bouquet_id = info['bouquet_id']
        if bouquet_id in stock and stock[bouquet_id] > 0:
            stock[bouquet_id] -= 1

        # Удалим данные пользователя после заказа
        del user_state[user_id]

    else:
        await update.message.reply_text("Я пока не понимаю эту команду. Попробуйте начать заказ сначала.")

# Инициализация
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback, pattern="order_"))
app.add_handler(CallbackQueryHandler(handle_date_time, pattern="date_.*|time_.*"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_user_info))

app.run_polling()

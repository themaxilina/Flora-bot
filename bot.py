
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = 519447526  # ← твой ID

main_menu = ReplyKeyboardMarkup(
    [['💐 Каталог', '🛍 Заказать'], ['📞 Контакты']],
    resize_keyboard=True
)

catalog_menu = ReplyKeyboardMarkup(
    [['🌹 Букет 1'], ['🌷 Букет 2'], ['🌻 Букет 3'], ['⬅️ Назад']],
    resize_keyboard=True
)

# Статусы пользователя
user_state = {}

# Остатки
stock = {
    "1": 0,
    "2": 2,
    "3": 10
}

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать в Flora Пермь! Выберите действие:",
        reply_markup=main_menu
    )

# Команды
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text

    if text == '💐 Каталог':
        await update.message.reply_text("Выберите букет:", reply_markup=catalog_menu)

    elif text == '🌹 Букет 1':
        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/0d3/nkr6256qhf6b79bdh86ezgl9kufycbei.jpeg",
            caption="🌹 Букет 1 — 18230₽\n❌ Нет в наличии",
        )

    elif text == '🌷 Букет 2':
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Заказать 🌷", callback_data="order_2")]])
        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/0fc/abo9003vbqn2fusdjosgknhsxwczpq7j.jpeg",
            caption=f"🌷 Букет 2 — 18230₽\nОсталось: {stock['2']} шт.",
            reply_markup=keyboard
        )

    elif text == '🌻 Букет 3':
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Заказать 🌻", callback_data="order_3")]])
        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/e25/f2bvr479poaj4h1qp9fx6o41slldkwqt.jpg",
            caption=f"🌻 Букет 3 — 32600₽\nОсталось: {stock['3']} шт.",
            reply_markup=keyboard
        )

    elif text == '⬅️ Назад':
        await update.message.reply_text("Вы вернулись в главное меню", reply_markup=main_menu)

    elif chat_id in user_state and user_state[chat_id]["step"] == "get_name_phone":
        user_state[chat_id]["contact"] = text

        await update.message.reply_text(
            f"Спасибо за заказ!\n\n"
            f"Букет: {user_state[chat_id]['bouquet']}\n"
            f"Дата: {user_state[chat_id]['date']}\n"
            f"Время: {user_state[chat_id]['time']}\n"
            f"Контакты: {text}"
        )

        # Уведомление админу
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                "🛎 Новый заказ!\n\n"
                f"Букет: {user_state[chat_id]['bouquet']}\n"
                f"Дата: {user_state[chat_id]['date']}\n"
                f"Время: {user_state[chat_id]['time']}\n"
                f"Контакты: {text}"
            )
        )

        # Уменьшаем остаток
        b_id = user_state[chat_id]["bouquet_id"]
        if b_id in stock and stock[b_id] > 0:
            stock[b_id] -= 1

        del user_state[chat_id]

    else:
        await update.message.reply_text("Я пока не понимаю эту команду 😊")

# Кнопки
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer()

    data = query.data

    if data.startswith("order_"):
        b_id = data.split("_")[1]

        if stock[b_id] <= 0:
            await query.message.reply_text("❌ Этот букет временно отсутствует.")
            return

        user_state[chat_id] = {
            "step": "get_date",
            "bouquet_id": b_id,
            "bouquet": f"Букет {b_id}"
        }

        dates = InlineKeyboardMarkup([
            [InlineKeyboardButton("24 апреля 2025", callback_data="date_24")],
            [InlineKeyboardButton("25 апреля 2025", callback_data="date_25")],
            [InlineKeyboardButton("26 апреля 2025", callback_data="date_26")],
        ])
        await query.message.reply_text("Выберите дату доставки:", reply_markup=dates)

    elif data.startswith("date_"):
        date_text = data.split("_")[1]
        dates_map = {
            "24": "24 апреля 2025",
            "25": "25 апреля 2025",
            "26": "26 апреля 2025"
        }

        if chat_id in user_state:
            user_state[chat_id]["date"] = dates_map[date_text]
            user_state[chat_id]["step"] = "get_time"

            times = InlineKeyboardMarkup([
                [InlineKeyboardButton("10:00–12:00", callback_data="time_morning")],
                [InlineKeyboardButton("12:00–15:00", callback_data="time_day")],
                [InlineKeyboardButton("15:00–18:00", callback_data="time_evening")],
            ])
            await query.message.reply_text("Выберите время доставки:", reply_markup=times)

    elif data.startswith("time_"):
        times_map = {
            "morning": "10:00–12:00",
            "day": "12:00–15:00",
            "evening": "15:00–18:00"
        }
        time = data.split("_")[1]

        if chat_id in user_state:
            user_state[chat_id]["time"] = times_map[time]
            user_state[chat_id]["step"] = "get_name_phone"
            await query.message.reply_text("Пожалуйста, введите ваше имя и номер телефона:")

# Запуск
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.run_polling()

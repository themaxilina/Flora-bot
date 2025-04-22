
import logging
import os
from telegram import (
    Update, ReplyKeyboardMarkup,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from datetime import datetime, timedelta

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

# Хранение состояния пользователя
user_state = {}

# Остатки
stock = {
    "1": 0,  # Нет в наличии
    "2": 2,  # 2 штуки
    "3": 999  # Много
}

# Формируем 3 ближайших даты
def get_delivery_dates():
    return [(datetime.now() + timedelta(days=i)).strftime("%d.%m.%Y") for i in range(1, 4)]

time_slots = ['10:00–12:00', '12:00–15:00', '15:00–18:00']

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать в Flora Пермь! Выберите действие:",
        reply_markup=main_menu
    )

# Каталог
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id

    if text == '💐 Каталог':
        await update.message.reply_text("Выберите букет:", reply_markup=catalog_menu)

    elif text == '🌹 Букет 1':
        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/0d3/nkr6256qhf6b79bdh86ezgl9kufycbei.jpeg",
            caption="🌹 Букет 1 — 18230₽\n\n❌ Временно нет в наличии."
        )

    elif text == '🌷 Букет 2':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Заказать 🌷", callback_data="order_2")]
        ])
        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/0fc/abo9003vbqn2fusdjosgknhsxwczpq7j.jpeg",
            caption=f"🌷 Букет 2 — 18230₽\n\nОсталось: {stock['2']} шт.",
            reply_markup=keyboard
        )

    elif text == '🌻 Букет 3':
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Заказать 🌻", callback_data="order_3")]
        ])
        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/e25/f2bvr479poaj4h1qp9fx6o41slldkwqt.jpg",
            caption="🌻 Букет 3 — 32600₽",
            reply_markup=keyboard
        )

    elif text == '⬅️ Назад':
        await update.message.reply_text("Вы вернулись в главное меню", reply_markup=main_menu)

    elif text == '🛍 Заказать':
        await update.message.reply_text(
            "Чтобы оформить заказ:\n"
            "1. Перейдите в 💐 Каталог\n"
            "2. Выберите букет\n"
            "3. Нажмите кнопку 'Заказать' под ним"
        )

    elif text == '📞 Контакты':
        await update.message.reply_text(
            "📍 Пермь, Карпинского 91д\n📞 +7 (342) 214-88-99\n⏰ 9:00–21:00"
        )

    else:
        if chat_id in user_state and user_state[chat_id]["step"] == "get_name_phone":
            user_state[chat_id]["contact"] = text
            await update.message.reply_text(
                f"Спасибо за заказ!\n\n"
                f"Букет: {user_state[chat_id]['bouquet']}\n"
                f"Дата: {user_state[chat_id]['date']}\n"
                f"Время: {user_state[chat_id]['time']}\n"
                f"Контакты: {text}"
            )
            # Обновляем остатки
            b_id = user_state[chat_id]["bouquet_id"]
            if b_id in stock and stock[b_id] > 0:
                stock[b_id] -= 1
            del user_state[chat_id]
        else:
            await update.message.reply_text("Я пока не понимаю эту команду 😊")

# Обработка inline-кнопок
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    bouquet_id = query.data.split("_")[1]
    if stock[bouquet_id] == 0:
        await query.message.reply_text("❌ Этот букет временно недоступен.")
        return

    bouquet_names = {"2": "🌷 Букет 2", "3": "🌻 Букет 3"}
    user_state[chat_id] = {
        "step": "choose_date",
        "bouquet": bouquet_names[bouquet_id],
        "bouquet_id": bouquet_id
    }

    buttons = [[InlineKeyboardButton(date, callback_data=f"date_{date}")] for date in get_delivery_dates()]
    markup = InlineKeyboardMarkup(buttons)
    await query.message.reply_text(
        f"Вы выбрали {bouquet_names[bouquet_id]}.\nВыберите дату доставки:",
        reply_markup=markup
    )

# Обработка выбора даты и времени
async def handle_next_steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    data = query.data

    if chat_id not in user_state:
        await query.message.reply_text("Пожалуйста, начните заказ заново.")
        return

    if data.startswith("date_"):
        chosen_date = data.split("_")[1]
        user_state[chat_id]["date"] = chosen_date
        user_state[chat_id]["step"] = "choose_time"

        buttons = [[InlineKeyboardButton(t, callback_data=f"time_{t}")] for t in time_slots]
        await query.message.reply_text("Выберите время доставки:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("time_"):
        chosen_time = data.split("_")[1]
        user_state[chat_id]["time"] = chosen_time
        user_state[chat_id]["step"] = "get_name_phone"
        await query.message.reply_text("Пожалуйста, введите ваше имя и номер телефона:")

# Запуск
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_next_steps, pattern="^(date_|time_)"))
app.add_handler(CallbackQueryHandler(handle_callback, pattern="^order_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.run_polling()

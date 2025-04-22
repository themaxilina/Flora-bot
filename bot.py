
import logging
import os
from telegram import (
    Update, ReplyKeyboardMarkup, InlineKeyboardMarkup,
    InlineKeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)

# Токен
TOKEN = os.environ.get("BOT_TOKEN")

# Главное меню
main_menu = ReplyKeyboardMarkup(
    [['💐 Каталог', '🛍 Заказать'], ['📞 Контакты']],
    resize_keyboard=True
)

# Каталог
catalog_menu = ReplyKeyboardMarkup(
    [['🌹 Букет 1'], ['🌷 Букет 2'], ['🌻 Букет 3'], ['⬅️ Назад']],
    resize_keyboard=True
)

# Даты доставки
delivery_dates = ["Сегодня", "Завтра", "Послезавтра"]
delivery_times = ["10:00 – 13:00", "13:00 – 17:00", "17:00 – 20:00"]

# Хранилище состояний пользователей
user_state = {}

# Букеты и их наличие
bouquets = {
    "1": {"name": "🌹 Букет 1", "price": "18230₽", "photo": "https://floraservis.ru/upload/iblock/0d3/nkr6256qhf6b79bdh86ezgl9kufycbei.jpeg", "available": False},
    "2": {"name": "🌷 Букет 2", "price": "18230₽", "photo": "https://floraservis.ru/upload/iblock/0fc/abo9003vbqn2fusdjosgknhsxwczpq7j.jpeg", "available": True},
    "3": {"name": "🌻 Букет 3", "price": "32600₽", "photo": "https://floraservis.ru/upload/iblock/e25/f2bvr479poaj4h1qp9fx6o41slldkwqt.jpg", "available": True},
}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать в Flora Пермь! Выберите действие:", reply_markup=main_menu)

# Кнопки из каталога
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == '💐 Каталог':
        await update.message.reply_text("Выберите букет:", reply_markup=catalog_menu)

    elif text == '⬅️ Назад':
        await update.message.reply_text("Вы вернулись в главное меню", reply_markup=main_menu)

    elif text == '📞 Контакты':
        await update.message.reply_text("📍 Пермь, Карпинского 91д\n📞 +7 (342) 214-88-99\n⏰ 9:00–21:00")

    elif text.startswith('🌹') or text.startswith('🌷') or text.startswith('🌻'):
        bouquet_id = text.split()[-1]
        data = bouquets.get(bouquet_id)

        if not data:
            await update.message.reply_text("Такого букета нет.")
            return

        if not data["available"]:
            await update.message.reply_text(f"{data['name']} временно нет в наличии.")
            return

        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"Заказать {data['name']}", callback_data=f"order_{bouquet_id}")]])
        await update.message.reply_photo(photo=data['photo'], caption=f"{data['name']} — {data['price']}", reply_markup=keyboard)

    elif user_id in user_state:
        step = user_state[user_id].get("step")
        if step == "name":
            user_state[user_id]["name"] = text
            user_state[user_id]["step"] = "phone"
            await update.message.reply_text("Введите ваш номер телефона:")
        elif step == "phone":
            user_state[user_id]["phone"] = text
            user_state[user_id]["step"] = "date"
            buttons = [[InlineKeyboardButton(d, callback_data=f"date_{d}")] for d in delivery_dates]
            await update.message.reply_text("Выберите дату доставки:", reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await update.message.reply_text("Я пока не понимаю эту команду 😊")
    else:
        await update.message.reply_text("Я пока не понимаю эту команду 😊")

# Кнопка "Заказать букет"
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data.startswith("order_"):
        bouquet_id = query.data.split("_")[1]
        data = bouquets.get(bouquet_id)

        if not data or not data["available"]:
            await query.message.reply_text(f"{data['name']} временно недоступен.")
            return

        # Сохраняем выбор букета
        user_state[user_id] = {
            "step": "name",
            "bouquet_id": bouquet_id,
            "bouquet_name": data["name"]
        }
        await query.message.reply_text(f"Вы выбрали {data['name']}. Введите ваше имя:")

    elif query.data.startswith("date_"):
        date = query.data.split("_")[1]
        user_state[user_id]["date"] = date
        user_state[user_id]["step"] = "time"
        buttons = [[InlineKeyboardButton(t, callback_data=f"time_{t}")] for t in delivery_times]
        await query.message.reply_text("Выберите удобное время доставки:", reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data.startswith("time_"):
        time = query.data.split("_")[1]
        state = user_state.get(user_id, {})
        state["time"] = time

        # Завершаем заказ
        summary = (
            f"Спасибо за заказ!\n\n"
            f"Букет: {state.get('bouquet_name')}\n"
            f"Имя: {state.get('name')}\n"
            f"Телефон: {state.get('phone')}\n"
            f"Дата: {state.get('date')}\n"
            f"Время: {state.get('time')}"
        )

        await query.message.reply_text(summary, reply_markup=main_menu)
        user_state.pop(user_id, None)  # очищаем

# Запуск
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()

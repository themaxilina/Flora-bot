
import logging
import os
from telegram import (
    Update, ReplyKeyboardMarkup, InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота из переменных окружения
TOKEN = os.environ.get("BOT_TOKEN")

# Главное меню
main_menu = ReplyKeyboardMarkup(
    [['💐 Каталог', '🛍 Заказать'], ['📞 Контакты']],
    resize_keyboard=True
)

# Меню каталога
catalog_menu = ReplyKeyboardMarkup(
    [['🌹 Букет 1'], ['🌷 Букет 2'], ['🌻 Букет 3'], ['⬅️ Назад']],
    resize_keyboard=True
)

# Состояние пользователей
user_state = {}

# Остатки по букетам
stock = {"1": 0, "2": 3, "3": 3}  # Букет 1 нет в наличии

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать в Flora Пермь! Выберите действие:",
        reply_markup=main_menu
    )

# Кнопки даты
def date_keyboard(bouquet_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Сегодня", callback_data=f"date_today_{bouquet_id}"),
            InlineKeyboardButton("Завтра", callback_data=f"date_tomorrow_{bouquet_id}"),
            InlineKeyboardButton("Послезавтра", callback_data=f"date_after_{bouquet_id}")
        ]
    ])

# Кнопки времени
def time_keyboard(bouquet_id, date_key):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("09:00–12:00", callback_data=f"time_morning_{bouquet_id}_{date_key}"),
            InlineKeyboardButton("12:00–15:00", callback_data=f"time_day_{bouquet_id}_{date_key}"),
            InlineKeyboardButton("15:00–18:00", callback_data=f"time_evening_{bouquet_id}_{date_key}")
        ]
    ])

# Обработка сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if text == '💐 Каталог':
        await update.message.reply_text("Выберите букет:", reply_markup=catalog_menu)

    elif text == '⬅️ Назад':
        await update.message.reply_text("Вы вернулись в главное меню", reply_markup=main_menu)

    elif text == '📞 Контакты':
        await update.message.reply_text("📍 Пермь, Карпинского 91д\n📞 +7 (342) 214-88-99\n⏰ 9:00–21:00")

    elif text in ['🌹 Букет 1', '🌷 Букет 2', '🌻 Букет 3']:
        b_id = text.split(" ")[1]
        photo_urls = {
            "1": "https://floraservis.ru/upload/iblock/0d3/nkr6256qhf6b79bdh86ezgl9kufycbei.jpeg",
            "2": "https://floraservis.ru/upload/iblock/0fc/abo9003vbqn2fusdjosgknhsxwczpq7j.jpeg",
            "3": "https://floraservis.ru/upload/iblock/e25/f2bvr479poaj4h1qp9fx6o41slldkwqt.jpg"
        }
        captions = {
            "1": "🌹 Букет 1 — 18230₽",
            "2": "🌷 Букет 2 — 18230₽",
            "3": "🌻 Букет 3 — 32600₽"
        }

        if stock[b_id] == 0:
            await update.message.reply_photo(
                photo=photo_urls[b_id],
                caption=f"{captions[b_id]}\n\n❌ Нет в наличии"
            )
        else:
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Заказать", callback_data=f"order_{b_id}")]]
            )
            await update.message.reply_photo(
                photo=photo_urls[b_id],
                caption=captions[b_id],
                reply_markup=keyboard
            )

    elif text == '🛍 Заказать':
        await update.message.reply_text("Для заказа выберите букет в каталоге.")

    # Проверка: если ожидается имя и телефон
    elif user_id in user_state and "time" in user_state[user_id]:
        await collect_user_info(update, context)

    else:
        await update.message.reply_text("Я пока не понимаю эту команду 😊")

# Обработка кнопок
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("order_"):
        bouquet_id = data.split("_")[1]

        if stock[bouquet_id] == 0:
            await query.message.reply_text("❌ Букет временно недоступен.")
            return

        user_state[user_id] = {"bouquet_id": bouquet_id}
        await query.message.reply_text("Выберите дату доставки:", reply_markup=date_keyboard(bouquet_id))

    elif data.startswith("date_"):
        _, date_key, bouquet_id = data.split("_")
        user_state[user_id]["date"] = date_key
        await query.message.reply_text("Выберите время доставки:", reply_markup=time_keyboard(bouquet_id, date_key))

    elif data.startswith("time_"):
        _, time_key, bouquet_id, date_key = data.split("_")
        user_state[user_id]["time"] = time_key
        await query.message.reply_text("Введите ваше имя и номер телефона:")

# Получение контактов и финальное сообщение
async def collect_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_state:
        await update.message.reply_text("Пожалуйста, начните заказ заново.")
        return

    info = user_state[user_id]

    if "bouquet_id" not in info or "date" not in info or "time" not in info:
        await update.message.reply_text("Сначала выберите букет, дату и время.")
        return

    info["contact"] = text

    bouquet_names = {"1": "🌹 Букет 1", "2": "🌷 Букет 2", "3": "🌻 Букет 3"}
    time_names = {"morning": "09:00–12:00", "day": "12:00–15:00", "evening": "15:00–18:00"}
    date_names = {"today": "Сегодня", "tomorrow": "Завтра", "after": "Послезавтра"}

    await update.message.reply_text(
        f"Спасибо за заказ!\n\n"
        f"{bouquet_names.get(info['bouquet_id'])}\n"
        f"Дата: {date_names.get(info['date'])}\n"
        f"Время: {time_names.get(info['time'])}\n"
        f"Контакты: {info['contact']}"
    )

    # Уменьшаем остаток
    if stock[info['bouquet_id']] > 0:
        stock[info['bouquet_id']] -= 1

    del user_state[user_id]

# Запуск бота
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()

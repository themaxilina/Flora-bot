
import logging
import os
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Логгирование
logging.basicConfig(level=logging.INFO)

# Токен бота из переменной окружения
TOKEN = os.environ.get("BOT_TOKEN")

# Меню
main_menu = ReplyKeyboardMarkup(
    [['💐 Каталог', '🛍 Заказать'], ['📞 Контакты']],
    resize_keyboard=True
)

catalog_menu = ReplyKeyboardMarkup(
    [['🌹 Букет 1'], ['🌷 Букет 2'], ['🌻 Букет 3'], ['⬅️ Назад']],
    resize_keyboard=True
)

# Состояния
user_data = {}
availability = {"1": 0, "2": 2, "3": 10}

date_options = ["24 апреля 2025", "25 апреля 2025", "26 апреля 2025"]
time_slots = ["с 9:00 до 12:00", "с 12:00 до 15:00", "с 15:00 до 18:00"]

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать в Flora Пермь! Выберите действие:",
        reply_markup=main_menu
    )

# Обработка текстовых сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    # Если пользователь на этапе ввода имени и телефона
    if user_id in user_data and user_data[user_id].get("waiting_for") == "name_phone":
        user_data[user_id]["name_phone"] = text
        bouquet = user_data[user_id]["bouquet"]
        date = user_data[user_id]["date"]
        time = user_data[user_id]["time"]
        name_phone = user_data[user_id]["name_phone"]

        await update.message.reply_text(
            f"Спасибо за заказ!\n\n"
            f"Букет: {bouquet}\n"
            f"Дата доставки: {date}\n"
            f"Время: {time}\n"
            f"Имя и телефон: {name_phone}"
        )
        del user_data[user_id]
        return

    # Обычная логика
    if text == '💐 Каталог':
        await update.message.reply_text("Выберите букет:", reply_markup=catalog_menu)

    elif text == '⬅️ Назад':
        await update.message.reply_text("Вы вернулись в главное меню", reply_markup=main_menu)

    elif text == '📞 Контакты':
        await update.message.reply_text(
            "📍 Пермь, Карпинского 91д\n📞 +7 (342) 214-88-99\n⏰ 9:00–21:00"
        )

    elif text == '🛍 Заказать':
        await update.message.reply_text("Выберите букет в Каталоге и нажмите 'Заказать'")

    elif text == '🌹 Букет 1':
        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/0d3/nkr6256qhf6b79bdh86ezgl9kufycbei.jpeg",
            caption="🌹 Букет 1 — 18230₽\n❌ Нет в наличии"
        )

    elif text == '🌷 Букет 2':
        count = availability["2"]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Заказать 🌷", callback_data="order_2")]
        ])
        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/0fc/abo9003vbqn2fusdjosgknhsxwczpq7j.jpeg",
            caption=f"🌷 Букет 2 — 18230₽\nВ наличии: {count} шт.",
            reply_markup=keyboard
        )

    elif text == '🌻 Букет 3':
        count = availability["3"]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Заказать 🌻", callback_data="order_3")]
        ])
        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/e25/f2bvr479poaj4h1qp9fx6o41slldkwqt.jpg",
            caption=f"🌻 Букет 3 — 32600₽\nВ наличии: {count} шт.",
            reply_markup=keyboard
        )

    else:
        await update.message.reply_text("Я пока не понимаю эту команду 😊")

# Обработка кнопок "Заказать"
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    action = query.data

    if action.startswith("order_"):
        bouquet_id = action.split("_")[1]

        if availability[bouquet_id] == 0:
            await query.message.reply_text("❌ К сожалению, этого букета нет в наличии.")
            return

        # Сохраняем выбор
        names = {"1": "🌹 Букет 1", "2": "🌷 Букет 2", "3": "🌻 Букет 3"}
        user_data[user_id] = {
            "bouquet_id": bouquet_id,
            "bouquet": names[bouquet_id],
        }

        # Кнопки с датами
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(date, callback_data=f"date_{date}")] for date in date_options
        ])
        await query.message.reply_text("Выберите дату доставки:", reply_markup=keyboard)

    elif action.startswith("date_"):
        date = action.split("date_")[1]
        user_data[user_id]["date"] = date

        # Кнопки с временем
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t, callback_data=f"time_{t}")] for t in time_slots
        ])
        await query.message.reply_text("Выберите удобное время:", reply_markup=keyboard)

    elif action.startswith("time_"):
        time = action.split("time_")[1]
        user_data[user_id]["time"] = time
        user_data[user_id]["waiting_for"] = "name_phone"

        await query.message.reply_text("Пожалуйста, отправьте ваше имя и номер телефона:")

# Обработка ошибок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("Exception while handling an update:", exc_info=context.error)
    if update and hasattr(update, "message") and update.message:
        await update.message.reply_text("Произошла ошибка. Мы уже разбираемся!")

# Запуск приложения
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.add_error_handler(error_handler)

app.run_polling()

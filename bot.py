
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")
admin_id = 519447526

# Остатки букетов
stock = {
    "1": 0,
    "2": 2,
    "3": 10
}

# Главное меню
main_menu = ReplyKeyboardMarkup(
    [['💐 Каталог', '🛍 Заказать'], ['📞 Контакты']],
    resize_keyboard=True
)

catalog_menu = ReplyKeyboardMarkup(
    [['🌹 Букет 1'], ['🌷 Букет 2'], ['🌻 Букет 3'], ['⬅️ Назад']],
    resize_keyboard=True
)

user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать в Flora Пермь! Выберите действие:", reply_markup=main_menu)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # Шаги заказа: если пользователь выбирает имя
    if user_id in user_state and user_state[user_id]["step"] == "wait_name":
        user_state[user_id]["name"] = text
        user_state[user_id]["step"] = "wait_phone"
        await update.message.reply_text("Пожалуйста, введите ваш номер телефона:")
        return

    # Если пользователь отправляет номер телефона
    elif user_id in user_state and user_state[user_id]["step"] == "wait_phone":
        user_state[user_id]["phone"] = text
        data = user_state[user_id]

        # Уменьшаем количество букетов
        stock[data["bouquet"]] -= 1

        # Сообщение админу
        admin_msg = (
            f"🎉 Новый заказ!\n"
            f"Букет: {data['bouquet_name']}\n"
            f"Дата: {data['date']}\n"
            f"Время: {data['time']}\n"
            f"Имя: {data['name']}\n"
            f"Телефон: {data['phone']}"
        )
        await context.bot.send_message(chat_id=admin_id, text=admin_msg)

        # Подтверждение пользователю
        await update.message.reply_text(
            f"Спасибо за заказ!\n"
            f"Букет: {data['bouquet_name']}\nДата: {data['date']}\nВремя: {data['time']}\n"
            f"Мы скоро с вами свяжемся!"
        )
        user_state.pop(user_id, None)
        return

    if text == '💐 Каталог':
        await update.message.reply_text("Выберите букет:", reply_markup=catalog_menu)

    elif text.startswith('🌹 Букет 1'):
        await send_bouquet_info(update, "1", "🌹 Букет 1", "https://floraservis.ru/upload/iblock/0d3/nkr6256qhf6b79bdh86ezgl9kufycbei.jpeg")

    elif text.startswith('🌷 Букет 2'):
        await send_bouquet_info(update, "2", "🌷 Букет 2", "https://floraservis.ru/upload/iblock/0fc/abo9003vbqn2fusdjosgknhsxwczpq7j.jpeg")

    elif text.startswith('🌻 Букет 3'):
        await send_bouquet_info(update, "3", "🌻 Букет 3", https://floraservis.ru/upload/iblock/e25/f2bvr479poaj4h1qp9fx6o41slldkwqt.jpg)   
    elif text == '⬅️ Назад':
        await update.message.reply_text("Вы вернулись в главное меню", reply_markup=main_menu)

    elif text == '🛍 Заказать':
        await update.message.reply_text("Пожалуйста, выберите букет из каталога для оформления заказа.")

    elif text == '📞 Контакты':
        await update.message.reply_text("📍 Пермь, Карпинского 91д\n📞 +7 (342) 214-88-99\n⏰ 9:00–21:00")

    else:
        await update.message.reply_text("Я пока не понимаю эту команду 😊")

async def send_bouquet_info(update, code, name, photo_url):
    count = stock[code]
    if count <= 0:
        await update.message.reply_photo(
            photo=photo_url,
            caption=f"{name}\n❌ Временно нет в наличии"
        )
    else:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Заказать", callback_data=f"order_{code}")]])
        await update.message.reply_photo(
            photo=photo_url,
            caption=f"{name}\nОсталось: {count} шт.",
            reply_markup=keyboard
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data.split("_")[1]
    names = {"1": "🌹 Букет 1", "2": "🌷 Букет 2", "3": "🌻 Букет 3"}
    name = names.get(data, "Букет")

    if stock[data] <= 0:
        await query.message.reply_text(f"{name} временно нет в наличии.")
        return

    # Запоминаем заказ
    user_state[user_id] = {
        "bouquet": data,
        "bouquet_name": name,
        "step": "select_date"
    }

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("24 апреля 2025", callback_data="date_24"),
         InlineKeyboardButton("25 апреля 2025", callback_data="date_25"),
         InlineKeyboardButton("26 апреля 2025", callback_data="date_26")]
    ])
    await query.message.reply_text("Выберите дату доставки:", reply_markup=keyboard)

# Обработка даты и времени
async def handle_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    data = query.data

    if user_id not in user_state:
        await query.message.reply_text("Пожалуйста, начните заказ заново.")
        return

    if data.startswith("date_"):
        date = data.split("_")[1]
        date_text = {
            "24": "24 апреля 2025",
            "25": "25 апреля 2025",
            "26": "26 апреля 2025"
        }.get(date, "")
        user_state[user_id]["date"] = date_text
        user_state[user_id]["step"] = "select_time"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("9:00 – 12:00", callback_data="time_morning")],
            [InlineKeyboardButton("12:00 – 16:00", callback_data="time_day")],
            [InlineKeyboardButton("16:00 – 20:00", callback_data="time_evening")]
        ])
        await query.message.reply_text("Выберите время доставки:", reply_markup=keyboard)

    elif data.startswith("time_"):
        time = {
            "morning": "9:00 – 12:00",
            "day": "12:00 – 16:00",
            "evening": "16:00 – 20:00"
        }.get(data.split("_")[1], "")
        user_state[user_id]["time"] = time
        user_state[user_id]["step"] = "wait_name"
        await query.message.reply_text("Пожалуйста, введите ваше имя:")

# Запуск бота
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback, pattern="^order_"))
app.add_handler(CallbackQueryHandler(handle_inline, pattern="^(date_|time_)"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()

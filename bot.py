
import logging
import os
from datetime import datetime, timedelta
from telegram import (
    Update, ReplyKeyboardMarkup, InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")  # Подставь свой токен
ADMIN_ID = 519447526  # Твой Telegram user ID

# Наличие букетов
stock = {
    "1": 0,
    "2": 2,
    "3": 5
}

# Данные заказов
user_order_data = {}

main_menu = ReplyKeyboardMarkup(
    [['💐 Каталог', '🛍 Заказать'], ['📞 Контакты']],
    resize_keyboard=True
)

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

# Каталог и выбор букетов
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '💐 Каталог':
        await update.message.reply_text("Выберите букет:", reply_markup=catalog_menu)

    elif text == '🌹 Букет 1':
        if stock["1"] == 0:
            await update.message.reply_photo(
                photo="https://floraservis.ru/upload/iblock/0d3/nkr6256qhf6b79bdh86ezgl9kufycbei.jpeg",
                caption="🌹 Букет 1 — 18230₽\n❌ Нет в наличии"
            )
        else:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Заказать 🌹", callback_data="order_1")]])
            await update.message.reply_photo(
                photo="https://floraservis.ru/upload/iblock/0d3/nkr6256qhf6b79bdh86ezgl9kufycbei.jpeg",
                caption=f"🌹 Букет 1 — 18230₽\nОсталось: {stock['1']}",
                reply_markup=keyboard
            )

    elif text == '🌷 Букет 2':
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Заказать 🌷", callback_data="order_2")]])
        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/0fc/abo9003vbqn2fusdjosgknhsxwczpq7j.jpeg",
            caption=f"🌷 Букет 2 — 18230₽\nОсталось: {stock['2']}",
            reply_markup=keyboard
        )

    elif text == '🌻 Букет 3':
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Заказать 🌻", callback_data="order_3")]])
        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/e25/f2bvr479poaj4h1qp9fx6o41slldkwqt.jpg",
            caption=f"🌻 Букет 3 — 32600₽\nОсталось: {stock['3']}",
            reply_markup=keyboard
        )

    elif text == '⬅️ Назад':
        await update.message.reply_text("Вы вернулись в главное меню", reply_markup=main_menu)

    elif text == '🛍 Заказать':
        await update.message.reply_text("Пожалуйста, выберите букет через каталог 🌸")

    elif text == '📞 Контакты':
        await update.message.reply_text(
            "📍 Пермь, Карпинского 91д\n📞 +7 (342) 214-88-99\n⏰ 9:00–21:00"
        )
    else:
        user_id = update.message.from_user.id
        if user_id in user_order_data and 'waiting_for' in user_order_data[user_id]:
            stage = user_order_data[user_id]['waiting_for']

            if stage == 'time':
                user_order_data[user_id]['time'] = text
                user_order_data[user_id]['waiting_for'] = 'name'
                await update.message.reply_text("Введите ваше имя:")

            elif stage == 'name':
                user_order_data[user_id]['name'] = text
                user_order_data[user_id]['waiting_for'] = 'phone'
                await update.message.reply_text("Введите ваш номер телефона:")

            elif stage == 'phone':
                user_order_data[user_id]['phone'] = text
                user_data = user_order_data[user_id]

                bouquet = user_data['bouquet']
                date = user_data['date']
                time = user_data['time']
                name = user_data['name']
                phone = user_data['phone']

                stock[bouquet] -= 1  # уменьшаем наличие

                msg = (
                    f"✅ Новый заказ!\n\n"
                    f"🌸 Букет №{bouquet}\n📅 Дата: {date}\n🕒 Время: {time}\n"
                    f"👤 Имя: {name}\n📞 Телефон: {phone}"
                )

                await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
                await update.message.reply_text("Спасибо за заказ! Мы с вами свяжемся 💐")

                del user_order_data[user_id]
            else:
                await update.message.reply_text("Что-то пошло не так. Попробуйте снова.")
        else:
            await update.message.reply_text("Я пока не понимаю эту команду 😊")

# Обработка кнопок "Заказать"
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    bouquet = query.data.split("_")[1]

    if stock[bouquet] == 0:
        await query.message.reply_text("❌ К сожалению, этот букет закончился.")
        return

    user_order_data[user_id] = {'bouquet': bouquet}

    # Выбор даты
    today = datetime.today()
    dates = [today + timedelta(days=i) for i in range(3)]
    buttons = [
        [InlineKeyboardButton(date.strftime("%d %B %Y"), callback_data=f"date_{date.strftime('%Y-%m-%d')}")]
        for date in dates
    ]
    await query.message.reply_text("Выберите дату доставки:", reply_markup=InlineKeyboardMarkup(buttons))

# Обработка выбора даты и времени
async def handle_date_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    data = query.data

    if data.startswith("date_"):
        date_str = data.split("_")[1]
        user_order_data[user_id]['date'] = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d %B %Y")
        user_order_data[user_id]['waiting_for'] = 'time'

        time_buttons = [
            [InlineKeyboardButton("09:00–12:00", callback_data="time_09:00–12:00")],
            [InlineKeyboardButton("12:00–15:00", callback_data="time_12:00–15:00")],
            [InlineKeyboardButton("15:00–18:00", callback_data="time_15:00–18:00")]
        ]
        await query.message.reply_text("Выберите время доставки:", reply_markup=InlineKeyboardMarkup(time_buttons))

    elif data.startswith("time_"):
        time_str = data.split("_")[1]
        user_order_data[user_id]['time'] = time_str
        user_order_data[user_id]['waiting_for'] = 'name'
        await query.message.reply_text("Введите ваше имя:")

# Запуск
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback, pattern="order_"))
app.add_handler(CallbackQueryHandler(handle_date_time, pattern="^(date_|time_)"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.run_polling()

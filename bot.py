
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

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать в Flora Пермь! Выберите действие:",
        reply_markup=main_menu
    )

# Обработка сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '💐 Каталог':
        await update.message.reply_text("Выберите букет:", reply_markup=catalog_menu)

    elif text == '🌹 Букет 1':
        await send_bouquet(update, "🌹 Букет 1", "18230₽", "https://floraservis.ru/upload/iblock/0d3/nkr6256qhf6b79bdh86ezgl9kufycbei.jpeg", "1")

    elif text == '🌷 Букет 2':
        await send_bouquet(update, "🌷 Букет 2", "18230₽", "https://floraservis.ru/upload/iblock/0fc/abo9003vbqn2fusdjosgknhsxwczpq7j.jpeg", "2")

    elif text == '🌻 Букет 3':
        await send_bouquet(update, "🌻 Букет 3", "32600₽", "https://floraservis.ru/upload/iblock/e25/f2bvr479poaj4h1qp9fx6o41slldkwqt.jpg", "3")

    elif text == '⬅️ Назад':
        await update.message.reply_text("Вы вернулись в главное меню", reply_markup=main_menu)

    elif text == '📞 Контакты':
        await update.message.reply_text(
            "📍 Пермь, Карпинского 91д\n📞 +7 (342) 214-88-99\n⏰ 9:00–21:00"
        )

    else:
        # Ожидание имени и телефона
        if context.user_data.get("waiting_for_contact"):
            context.user_data["contact_info"] = text
            await update.message.reply_text("Спасибо за заказ! Мы скоро свяжемся с вами 😊")

            # Можно сохранить в БД или вывести
            print("📝 Новый заказ:")
            print(context.user_data)

            context.user_data.clear()
        else:
            await update.message.reply_text("Я пока не понимаю эту команду 😊")

# Показ букета
async def send_bouquet(update, name, price, photo_url, code):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"Заказать {name}", callback_data=f"order_{code}")]])
    await update.message.reply_photo(photo=photo_url, caption=f"{name} — {price}", reply_markup=keyboard)

# Обработка кнопки "Заказать букет"
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    bouquet_id = query.data.split("_")[1]
    names = {"1": "🌹 Букет 1", "2": "🌷 Букет 2", "3": "🌻 Букет 3"}
    bouquet = names.get(bouquet_id, "Букет")

    context.user_data["bouquet"] = bouquet

    # Предложим выбрать дату
    today = datetime.today()
    dates = [(today + timedelta(days=i)).strftime("%d.%m.%Y") for i in range(3)]

    keyboard = [
        [InlineKeyboardButton(date, callback_data=f"date_{date}")] for date in dates
    ]
    await query.message.reply_text(
        f"Вы выбрали {bouquet}.\nПожалуйста, выберите дату доставки:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Обработка выбора даты и времени
async def handle_date_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("date_"):
        date = data.replace("date_", "")
        context.user_data["date"] = date

        times = ["10:00–13:00", "13:00–16:00", "16:00–19:00"]
        keyboard = [
            [InlineKeyboardButton(t, callback_data=f"time_{t}")] for t in times
        ]
        await query.message.reply_text(
            f"Вы выбрали дату: {date}. Теперь выберите удобное время:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("time_"):
        time = data.replace("time_", "")
        context.user_data["time"] = time
        context.user_data["waiting_for_contact"] = True

        await query.message.reply_text(
            f"Отлично! Вы выбрали доставку {context.user_data['date']} в {time}.\n\nПожалуйста, отправьте ваше имя и номер телефона:"
        )

# Запуск
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_date_time, pattern="^(date_|time_)"))
app.add_handler(CallbackQueryHandler(handle_callback, pattern="^order_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()

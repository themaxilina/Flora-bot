
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

main_menu = ReplyKeyboardMarkup(
    [['💐 Каталог', '🛍 Заказать'], ['📞 Контакты']],
    resize_keyboard=True
)

# Остатки
stock = {
    '2': 2  # Только у букета 2 — ограничение
}

# Состояния пользователей
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать в Flora Пермь! Выберите действие:",
        reply_markup=main_menu
    )

# Обработка сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if text == '💐 Каталог':
        catalog_text = "Выберите букет:\n\n"
        catalog_text += "🌹 Букет 1 — 18230₽ (❗ Нет в наличии)\n"
        if stock['2'] > 0:
            catalog_text += f"🌷 Букет 2 — 18230₽ (осталось {stock['2']} шт.)\n"
        else:
            catalog_text += "🌷 Букет 2 — 18230₽ (❗ Нет в наличии)\n"
        catalog_text += "🌻 Букет 3 — 32600₽\n"
        await update.message.reply_text(catalog_text)

    elif text == '🌹 Букет 1':
        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/0d3/nkr6256qhf6b79bdh86ezgl9kufycbei.jpeg",
            caption="🌹 Букет 1 — 18230₽\n❗ Временно нет в наличии."
        )

    elif text == '🌷 Букет 2':
        caption = "🌷 Букет 2 — 18230₽"
        if stock['2'] > 0:
            caption += f"\nОсталось: {stock['2']} шт."
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Заказать 🌷", callback_data="order_2")]])
        else:
            caption += "\n❗ Нет в наличии"
            keyboard = None

        await update.message.reply_photo(
            photo="https://floraservis.ru/upload/iblock/0fc/abo9003vbqn2fusdjosgknhsxwczpq7j.jpeg",
            caption=caption,
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

    elif text in ['24 апреля 2025', '25 апреля 2025', '26 апреля 2025']:
        user_data[user_id]['date'] = text
        await update.message.reply_text("Выберите время доставки:", reply_markup=ReplyKeyboardMarkup(
            [['9:00–12:00', '12:00–15:00', '15:00–18:00']], resize_keyboard=True
        ))

    elif text in ['9:00–12:00', '12:00–15:00', '15:00–18:00']:
        user_data[user_id]['time'] = text
        await update.message.reply_text("Введите ваше имя:")

    elif user_id in user_data and 'time' in user_data[user_id] and 'name' not in user_data[user_id]:
        user_data[user_id]['name'] = text
        await update.message.reply_text("Введите номер телефона:")

    elif user_id in user_data and 'name' in user_data[user_id] and 'phone' not in user_data[user_id]:
        user_data[user_id]['phone'] = text
        data = user_data[user_id]

        # Уменьшаем остаток
        if data['bouquet'] == "🌷 Букет 2" and stock['2'] > 0:
            stock['2'] -= 1

        await update.message.reply_text(
            f"Спасибо за заказ!\n\n"
            f"Букет: {data['bouquet']}\n"
            f"Дата доставки: {data['date']}\n"
            f"Время доставки: {data['time']}\n"
            f"Имя: {data['name']}\n"
            f"Телефон: {data['phone']}"
        )
        del user_data[user_id]

    else:
        await update.message.reply_text("Я пока не понимаю эту команду 😊")

# Обработка кнопки "Заказать"
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    bouquet_id = query.data.split("_")[1]
    bouquet_names = {"2": "🌷 Букет 2", "3": "🌻 Букет 3"}

    if bouquet_id == '2' and stock['2'] <= 0:
        await query.message.reply_text("❗ Букет 2 временно недоступен.")
        return

    user_data[user_id] = {'bouquet': bouquet_names[bouquet_id]}
    await query.message.reply_text("Вы выбрали " + bouquet_names[bouquet_id])
    await query.message.reply_text("Выберите дату доставки:", reply_markup=ReplyKeyboardMarkup(
        [['24 апреля 2025', '25 апреля 2025', '26 апреля 2025']], resize_keyboard=True
    ))

# Запуск бота
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.run_polling()

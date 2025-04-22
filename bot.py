
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Получаем токен из переменных окружения
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

# Хранилище состояний
user_state = {}
bouquet_stock = {'1': 0, '2': 5, '3': 5}  # Букет 1 — нет в наличии

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_state.pop(update.effective_chat.id, None)  # очищаем старые состояния
    await update.message.reply_text("Добро пожаловать в Flora Пермь! Выберите действие:", reply_markup=main_menu)

# Обработка каталога и кнопок
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id

    if text == '💐 Каталог':
        await update.message.reply_text("Выберите букет:", reply_markup=catalog_menu)

    elif text in ['🌹 Букет 1', '🌷 Букет 2', '🌻 Букет 3']:
        bouquet_id = text.split()[-1]
        user_state[chat_id] = {"bouquet": bouquet_id}

        # Проверка наличия
        if bouquet_stock.get(bouquet_id, 0) <= 0:
            await update.message.reply_photo(
                photo="https://floraservis.ru/upload/iblock/0d3/nkr6256qhf6b79bdh86ezgl9kufycbei.jpeg",
                caption=f"{text} — Нет в наличии"
            )
            return

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Заказать", callback_data=f"order_{bouquet_id}")]
        ])
        photo_url = {
            '1': "https://floraservis.ru/upload/iblock/0d3/nkr6256qhf6b79bdh86ezgl9kufycbei.jpeg",
            '2': "https://floraservis.ru/upload/iblock/0fc/abo9003vbqn2fusdjosgknhsxwczpq7j.jpeg",
            '3': "https://floraservis.ru/upload/iblock/e25/f2bvr479poaj4h1qp9fx6o41slldkwqt.jpg",
        }
        price = {'1': "18230₽", '2': "18230₽", '3': "32600₽"}

        await update.message.reply_photo(
            photo=photo_url[bouquet_id],
            caption=f"{text} — {price[bouquet_id]}",
            reply_markup=keyboard
        )

    elif text == '⬅️ Назад':
        await update.message.reply_text("Вы вернулись в главное меню", reply_markup=main_menu)

    elif text == '🛍 Заказать':
        await update.message.reply_text("Пожалуйста, выберите букет в каталоге для оформления заказа.")

    elif text == '📞 Контакты':
        await update.message.reply_text("📍 Пермь, Карпинского 91д\n📞 +7 (342) 214-88-99\n⏰ 9:00–21:00")

    # Логика сбора данных
    elif chat_id in user_state:
        state = user_state[chat_id]
        if "date" not in state:
            state["date"] = text
            await update.message.reply_text("Выберите удобное время доставки:", reply_markup=ReplyKeyboardMarkup(
                [['9:00–12:00', '12:00–15:00', '15:00–18:00']], resize_keyboard=True
            ))
        elif "time" not in state:
            state["time"] = text
            await update.message.reply_text("Введите ваше имя:")
        elif "name" not in state:
            state["name"] = text
            await update.message.reply_text("Введите ваш номер телефона:")
        elif "phone" not in state:
            state["phone"] = text
            await confirm_order(update, context, state)
            user_state.pop(chat_id)  # очищаем состояние после заказа
        else:
            await update.message.reply_text("Что-то пошло не так. Попробуйте оформить заказ заново.")
    else:
        await update.message.reply_text("Я пока не понимаю эту команду 😊")

# Обработка нажатия кнопки "Заказать"
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    bouquet_id = query.data.split("_")[1]
    user_state[chat_id] = {"bouquet": bouquet_id}

    await query.message.reply_text("Выберите дату доставки:", reply_markup=ReplyKeyboardMarkup(
        [['Сегодня', 'Завтра', 'Послезавтра']], resize_keyboard=True
    ))

# Подтверждение заказа
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE, state):
    bouquet_names = {'1': '🌹 Букет 1', '2': '🌷 Букет 2', '3': '🌻 Букет 3'}
    await update.message.reply_text(
        f"Спасибо за заказ!\n\n"
        f"{bouquet_names[state['bouquet']]}\n"
        f"Дата доставки: {state['date']}\n"
        f"Время: {state['time']}\n"
        f"Имя: {state['name']}\n"
        f"Телефон: {state['phone']}"
    )
    # Уменьшаем остаток
    bouquet_stock[state['bouquet']] -= 1

# Обработка ошибок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("Произошла ошибка:", exc_info=context.error)
    if update and hasattr(update, 'message') and update.message:
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

# Запуск приложения
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.add_error_handler(error_handler)
app.run_polling()

import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Загружаем переменные из .env файла
load_dotenv()

# Чтение токена и ID владельца из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция обработки команд /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Приветственное сообщение отправлено.")
    await update.message.reply_text("Бот запущен! Отправьте сообщение, и админ ответит в ближайшее время.")

# Функция пересылки сообщений владельцу
async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    text = update.message.text

    user_info = f"ID пользователя: {user_id}\nИмя пользователя: @{username if username else 'Нет'}\nСообщение: {text}"
    await context.bot.send_message(chat_id=OWNER_ID, text=user_info)
    await context.bot.send_message(chat_id=OWNER_ID, text=f"{user_id}")
    await update.message.reply_text("Ваше сообщение отправлено!")

# Функция обработки сообщений от владельца
async def reply_from_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        # Если сообщение от владельца, пересылаем его пользователю
        try:
            target_user_id = int(context.args[0])  # ID пользователя, указанный в первом аргументе команды
            message_to_send = " ".join(context.args[1:])  # Текст сообщения после ID
            await context.bot.send_message(chat_id=target_user_id, text=message_to_send)
        except (IndexError, ValueError):
            await update.message.reply_text("Использование: /reply <ID пользователя> <сообщение>")
    else:
        await update.message.reply_text("У вас нет прав для этой команды.")

def main():
    # Создание объекта приложения
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.User(user_id=OWNER_ID), forward_to_owner))
    application.add_handler(CommandHandler("reply", reply_from_owner))

    # Запуск бота
    logger.info("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()

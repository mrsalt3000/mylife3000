"""
Основной модуль запуска бота.

Инициализирует приложение, настраивает обработчики и запускает бота.
Использует dependency injection для передачи зависимостей.

Functions:
    post_init: Инициализация после создания приложения
    post_stop: Очистка ресурсов при остановке
    main: Основная функция запуска бота
"""

import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from .config import BOT_TOKEN, MAIN_MENU, SECTION_MENU, THEME, RESULT
from .handlers import start, handle_main_menu, handle_section_choice, handle_theme_choice, handle_result_choice, cancel
from .database import db
from .questionary import Questionary

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def post_init(application):
    """
    Инициализирует бота после создания приложения.
    
    Parameters
    ----------
    application : Application
        Экземпляр приложения Telegram Bot
    """
    
    await db.init_pool()
    
    # Инициализируем Questionary и сохраняем в bot_data для dependency injection
    questionary = Questionary()
    application.bot_data['questionary'] = questionary
    
    logger.info("Bot initialization completed")

async def post_stop(application):
    """
    Выполняет очистку ресурсов при остановке бота.
    
    Parameters
    ----------
    application : Application
        Экземпляр приложения Telegram Bot
    """

    await db.close()
    logger.info("Bot shutdown completed")

def main() -> None:
    """
    Основная функция запуска бота.
    
    Инициализирует приложение, настраивает обработчики диалога
    и запускает режим опроса (polling).
    """
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики инициализации и остановки
    application.post_init = post_init
    application.post_stop = post_stop

    # Создаем обработчик диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
            SECTION_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_section_choice)],
            THEME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_theme_choice)],
            RESULT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_result_choice)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

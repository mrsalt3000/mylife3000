#!/usr/bin/env python
# pylint: disable=unused-argument

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN, MAIN_MENU, SECTION_MENU, THEME, RESULT
from handlers import start, handle_main_menu, handle_section_choice, handle_theme_choice, handle_result_choice, cancel

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def main() -> None:
    """Запускает бота."""
    application = Application.builder().token(BOT_TOKEN).build()

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

if __name__ == "__main__":
    main()
#!/usr/bin/env python
# pylint: disable=unused-argument

import logging
import random
from typing import Dict

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Импортируем вопросы из отдельного файла
from questions_data import (
    QUESTIONS_MEMORIES, 
    QUESTIONS_SELF_KNOWLEDGE, 
    QUESTIONS_VECTOR, 
    QUESTIONS_CHALLENGES, 
    QUESTIONS_ENVIRONMENT, 
    QUESTIONS_INTEGRATION
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Определяем состояния диалога
MAIN_MENU, SECTION_MENU, THEME, RESULT = range(4)

# Словарь для связи названий разделов с соответствующими наборами вопросов
SECTION_QUESTIONS = {
    "Самопознание: Кто Я?": QUESTIONS_SELF_KNOWLEDGE,
    "Вектор: Куда я движусь?": QUESTIONS_VECTOR,
    "Вызовы: Что мне мешает?": QUESTIONS_CHALLENGES,
    "Окружение: Мои отношения?": QUESTIONS_ENVIRONMENT,
    "Интеграция: Как я живу?": QUESTIONS_INTEGRATION,
    "Капсула Времени: История для моих детей": QUESTIONS_MEMORIES
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает диалог и показывает главное меню."""
    reply_keyboard = [
        ["Самопознание: Кто Я?"], 
        ["Вектор: Куда я движусь?", "Вызовы: Что мне мешает?"],
        ["Окружение: Мои отношения?", "Интеграция: Как я живу?"],
        ["Капсула Времени: История для моих детей"],
        ["О проекте"]
    ]

    await update.message.reply_text(
        "Я предложу вам поразмышлять над вопросами о себе для саморазвтия и мемуаров\n\n"
        "Бот пока не умеет сохранять ответы.\n\n"
        "Отправьте /cancel чтобы завершить диалог.\n\n"
        "Выбери раздел:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, 
            one_time_keyboard=True, 
            input_field_placeholder="Выберите раздел"
        ),
    )
    return MAIN_MENU

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор в главном меню."""
    user_choice = update.message.text
    
    if user_choice in SECTION_QUESTIONS:
        context.user_data['current_section'] = user_choice
        context.user_data['current_questions'] = SECTION_QUESTIONS[user_choice]
        return await show_section_menu(update, context)
    elif user_choice == "О проекте":
        await update.message.reply_text(
            "Этот бот создан для саморазвития и создания мемуаров.\n\n"
            "Вопросы разделены на темы, чтобы помочь вам поразмышлять над разными аспектами жизни.\n\n"
            "Бот не сохраняет ваши ответы, поэтому вы можете быть откровенными.\n\n"
            "Нажмите /start чтобы вернуться в главное меню.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Пожалуйста, выберите один из предложенных разделов"
        )
        return MAIN_MENU

async def show_section_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показывает меню выбранного раздела."""
    section_name = context.user_data['current_section']
    questions = context.user_data['current_questions']
    
    # Определяем описание раздела
    section_descriptions = {
        "Самопознание: Кто Я?": "Самопознание: Кто Я? - это вопросы, помогающие понять свою личность, ценности и убеждения",
        "Вектор: Куда я движусь?": "Вектор: Куда я движусь? - вопросы о целях, мечтах и направлении жизни",
        "Вызовы: Что мне мешает?": "Вызовы: Что мне мешает? - вопросы о трудностях, страхах и ограничениях",
        "Окружение: Мои отношения?": "Окружение: Мои отношения? - вопросы о взаимодействии с людьми и социальной среде",
        "Интеграция: Как я живу?": "Интеграция: Как я живу? - вопросы о повседневной жизни, привычках и ритуалах",
        "Капсула Времени: История для моих детей": "Капсула Времени: История для моих детей - это то, что мы можем оставить себе будущему и потомкам"
    }
    
    description = section_descriptions.get(section_name, "Выберите действие:")
    
    reply_keyboard = [
        ["Случайный вопрос"],
        ["Выбрать тему"],
        ["Главное меню"]
    ]

    await update.message.reply_text(
        f"{description}\n\n"
        "Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, 
            one_time_keyboard=True, 
            input_field_placeholder="Выбор действия"
        ),
    )
    return SECTION_MENU

async def handle_section_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор в разделе."""
    user_choice = update.message.text
    questions = context.user_data.get('current_questions', {})
    
    if user_choice == "Главное меню":
        return await start(update, context)
    elif user_choice == "Случайный вопрос":
        if "Случайный вопрос" in questions:
            random_question = random.choice(questions["Случайный вопрос"])
        else:
            # Если нет специальной категории "Случайный вопрос", выбираем из всех вопросов раздела
            all_questions = []
            for theme_questions in questions.values():
                all_questions.extend(theme_questions)
            random_question = random.choice(all_questions)
            
        await update.message.reply_text(
            f"📖 {random_question}\n\n"
            "Хочешь еще вопрос? Отправь /start",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    elif user_choice == "Выбрать тему":
        return await theme_choice(update, context)
    else:
        await update.message.reply_text(
            "Пожалуйста, выбери один из предложенных вариантов"
        )
        return SECTION_MENU

async def theme_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Предлагает выбор темы."""
    questions = context.user_data.get('current_questions', {})
    themes = [key for key in questions.keys() if key != "Случайный вопрос"]
    reply_keyboard = [[theme] for theme in themes] + [["Назад", "Главное меню"]]

    await update.message.reply_text(
        "🎯 Выберите тему вопросов:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, 
            one_time_keyboard=True, 
            input_field_placeholder="Выбор темы"
        ),
    )
    return THEME

async def handle_theme_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор темы и показывает вопрос."""
    theme = update.message.text
    questions = context.user_data.get('current_questions', {})
    
    if theme == "Главное меню":
        return await start(update, context)
    elif theme == "Назад":
        return await show_section_menu(update, context)
    
    if theme in questions:
        question = random.choice(questions[theme])
        
        reply_keyboard = [
            ["Еще вопрос"], 
            ["Выбрать другую тему"], 
            ["Главное меню", "Завершить"]
        ]
        
        await update.message.reply_text(
            f"📖 {question}\n\n"
            "Что хотите сделать дальше?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, 
                one_time_keyboard=True
            )
        )
        context.user_data['last_theme'] = theme
        return RESULT
    else:
        themes = [key for key in questions.keys() if key != "Случайный вопрос"]
        reply_keyboard = [[theme] for theme in themes] + [["Назад", "Главное меню"]]
        
        await update.message.reply_text(
            "Пожалуйста, выберите одну из предложенных тем",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, 
                one_time_keyboard=True
            )
        )
        return THEME

async def handle_result_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор после показа вопроса."""
    choice = update.message.text
    questions = context.user_data.get('current_questions', {})
    
    if choice == "Главное меню":
        return await start(update, context)
    elif choice == "Завершить":
        await update.message.reply_text(
            "Спасибо за ответы! До встречи! 👋\n/start",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    last_theme = context.user_data.get('last_theme')
    if choice == "Еще вопрос":
        if last_theme and last_theme in questions:
            question = random.choice(questions[last_theme])
            
            reply_keyboard = [
                ["Еще вопрос"], 
                ["Выбрать другую тему"], 
                ["Главное меню", "Завершить"]
            ]
            
            await update.message.reply_text(
                f"📖 {question}\n\n"
                "Что хочешь сделать дальше?",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, 
                    one_time_keyboard=True
                )
            )
            return RESULT
        else:
            return await theme_choice(update, context)
    
    elif choice == "Выбрать другую тему":
        return await theme_choice(update, context)
    
    else:
        await update.message.reply_text(
            "Пожалуйста, выбери один из предложенных вариантов"
        )
        return RESULT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершает диалог."""
    await update.message.reply_text(
        "До встречи! 👋\n/start", 
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main() -> None:
    """Запускает бота."""
    application = Application.builder().token("8188231084:AAFaskYZTaFz2UnnQ91az0cTN3HX36U4YnQ").build()

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
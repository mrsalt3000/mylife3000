#!/usr/bin/env python
# pylint: disable=unused-argument

import logging
import random
from typing import Dict

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from config import (
    MAIN_MENU, SECTION_MENU, THEME, RESULT,
    SECTION_QUESTIONS, SECTION_DESCRIPTIONS,
    MAIN_MENU_KEYBOARD, SECTION_MENU_KEYBOARD, RESULT_MENU_KEYBOARD
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает диалог и показывает главное меню."""
    await update.message.reply_text(
        "Я предложу вам поразмышлять над вопросами о себе для саморазвтия и мемуаров\n\n"
        "Бот пока не умеет сохранять ответы.\n\n"
        "Отправьте /cancel чтобы завершить диалог.\n\n"
        "Выбери раздел:",
        reply_markup=ReplyKeyboardMarkup(
            MAIN_MENU_KEYBOARD, 
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
"""

Привет! 
Этот бот — твой личный проводник в мире саморефлексии. 
Мы собрали глубокие и иногда неожиданные вопросы, чтобы помочь тебе лучше узнать себя и создать живые мемуары, которые не напишешь по шаблону.

Как с этим работать? Всё просто:
    1. Выбирай тему, которая откликается тебе прямо сейчас.
    2. Получай карточку с вопросом. 
        Не торопись, дай себе время ощутить его.
    3. Отвечай так, как чувствуешь. 
        У нас нет готовых кнопок для ответа. 
        Ты можешь:
            • Записать мысли в свой бумажный дневник 📓
            • Наговорить искреннее голосовое сообщение 🎙️
            • Снять размышление на видео 🎥
            • Просто подумать над этим за чашкой чая ☕

Бот просто задаёт вопросы — твои ответы принадлежат только тебе.
Наша главная ценность — твоя конфиденциальность.
Бот НЕ сохраняет, НЕ анализирует и НЕ имеет доступа к твоим размышлениям. Ты можешь быть абсолютно откровенным.
Готов исследовать свои мысли? 
Жми /start!""",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Пожалуйста, выбери один из предложенных разделов"
        )
        return MAIN_MENU

async def show_section_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показывает меню выбранного раздела."""
    section_name = context.user_data['current_section']
    
    description = SECTION_DESCRIPTIONS.get(section_name, "Выбери действие:")

    await update.message.reply_text(
        f"{description}\n\n"
        "Выбери действие:",
        reply_markup=ReplyKeyboardMarkup(
            SECTION_MENU_KEYBOARD, 
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
        "🎯 Выбери тему вопросов:",
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
        
        await update.message.reply_text(
            f"📖 {question}\n\n"
            "Что хочешь сделать дальше?",
            reply_markup=ReplyKeyboardMarkup(
                RESULT_MENU_KEYBOARD, 
                one_time_keyboard=True
            )
        )
        context.user_data['last_theme'] = theme
        return RESULT
    else:
        themes = [key for key in questions.keys() if key != "Случайный вопрос"]
        reply_keyboard = [[theme] for theme in themes] + [["Назад", "Главное меню"]]
        
        await update.message.reply_text(
            "Пожалуйста, выбери одну из предложенных тем",
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
            
            await update.message.reply_text(
                f"📖 {question}\n\n"
                "Что хочешь сделать дальше?",
                reply_markup=ReplyKeyboardMarkup(
                    RESULT_MENU_KEYBOARD, 
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
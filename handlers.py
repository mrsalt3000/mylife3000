#!/usr/bin/env python
# pylint: disable=unused-argument

import logging
import random
from typing import Dict

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from config import (
    MAIN_MENU, SECTION_MENU, THEME, RESULT,
    MAIN_MENU_KEYBOARD, SECTION_MENU_KEYBOARD, RESULT_MENU_KEYBOARD
)
from database import db
from questionary import Questionary

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинает диалог и показывает главное меню."""
    user = update.effective_user
    
    try:
        # Логируем начало диалога в БД (без персональных данных)
        dialog_id = await db.start_dialog()
        context.user_data['dialog_id'] = dialog_id
        logger.info(f"Started dialog {dialog_id}")
        
    except Exception as e:
        logger.error(f"Error logging dialog start: {e}")
        # Продолжаем работу даже если логирование не удалось

    await update.message.reply_text(
        "Я предложу тебе поразмышлять над вопросами о себе для саморазвития и мемуаров\n\n"
        "Бот не сохраняет ответы и персональные данные.\n\n"
        "Отправь /cancel чтобы завершить диалог.\n\n"
        "Выбери раздел:",
        reply_markup=ReplyKeyboardMarkup(
            MAIN_MENU_KEYBOARD, 
            input_field_placeholder="Выбери раздел"
        ),
    )
    return MAIN_MENU

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор в главном меню."""
    user_choice = update.message.text
    
    questionary: Questionary = context.bot_data['questionary']
    
    if user_choice in questionary.get_all_sections():
        context.user_data['current_section'] = user_choice
        
        # Обновляем состояние диалога
        try:
            if 'dialog_id' in context.user_data:
                await db.update_dialog_state(context.user_data['dialog_id'], f'section_{user_choice}')
        except Exception as e:
            logger.error(f"Error updating dialog state: {e}")
            
        return await show_section_menu(update, context, questionary)
    elif user_choice == "О проекте":
        # Завершаем диалог при выборе "О проекте"
        await end_dialog(context, 'project_info')
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
            • Запись мыслей в свой бумажный дневник 📓
            • Наговорить искреннее голосовое сообщение 🎙️
            • Снять размышление на видео 🎥
            • Просто подумать над этим за чашкой чая ☕

Бот просто задаёт вопросы — твои ответы принадлежат только тебе.
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

async def show_section_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, questionary: Questionary) -> int:
    """Показывает меню выбранного раздела."""
    section_name = context.user_data['current_section']
    
    description = questionary.get_section_description(section_name)

    await update.message.reply_text(
        f"{description}\n\n"
        "Выбери действие:",
        reply_markup=ReplyKeyboardMarkup(
            SECTION_MENU_KEYBOARD, 
            input_field_placeholder="Выбор действия"
        ),
    )
    return SECTION_MENU

async def handle_section_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор в разделе."""
    user_choice = update.message.text
    questionary: Questionary = context.bot_data['questionary']
    section_name = context.user_data.get('current_section')
    
    if user_choice == "Главное меню":
        return await start(update, context)
    elif user_choice == "Случайный вопрос":
        if section_name:
            random_question = questionary.get_random_question(section_name)
            if random_question:
                await update.message.reply_text(
                    f"📖 {random_question}\n\n"
                    "Хочешь еще вопрос? Отправь /start",
                    reply_markup=ReplyKeyboardRemove()
                )
                await end_dialog(context, 'random_question')
                return ConversationHandler.END
        
        # Если что-то пошло не так
        await update.message.reply_text(
            "Произошла ошибка при выборе вопроса. Попробуй еще раз.",
            reply_markup=ReplyKeyboardMarkup(SECTION_MENU_KEYBOARD)
        )
        return SECTION_MENU
    elif user_choice == "Выбрать тему":
        return await theme_choice(update, context, questionary)
    else:
        await update.message.reply_text(
            "Пожалуйста, выбери один из предложенных вариантов"
        )
        return SECTION_MENU

async def theme_choice(update: Update, context: ContextTypes.DEFAULT_TYPE, questionary: Questionary) -> int:
    """Предлагает выбор темы."""
    section_name = context.user_data.get('current_section')
    if not section_name:
        return await start(update, context)
        
    themes = questionary.get_themes(section_name)
    reply_keyboard = [[theme] for theme in themes] + [["Назад", "Главное меню"]]

    await update.message.reply_text(
        "🎯 Выбери тему вопросов:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, 
            input_field_placeholder="Выбор темы"
        ),
    )
    return THEME

async def handle_theme_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор темы и показывает вопрос."""
    theme = update.message.text
    questionary: Questionary = context.bot_data['questionary']
    section_name = context.user_data.get('current_section')
    
    if not section_name:
        return await start(update, context)
    
    if theme == "Главное меню":
        return await start(update, context)
    elif theme == "Назад":
        return await show_section_menu(update, context, questionary)
    
    # Проверяем, что тема существует в выбранном разделе
    themes = questionary.get_themes(section_name)
    if theme in themes:
        question = questionary.get_random_question(section_name, theme)
        
        if question:
            # Обновляем состояние диалога
            try:
                if 'dialog_id' in context.user_data:
                    await db.update_dialog_state(context.user_data['dialog_id'], f'theme_{theme}')
            except Exception as e:
                logger.error(f"Error updating dialog state: {e}")
            
            await update.message.reply_text(
                f"📖 {question}\n\n"
                "Что хочешь сделать дальше?",
                reply_markup=ReplyKeyboardMarkup(RESULT_MENU_KEYBOARD)
            )
            context.user_data['last_theme'] = theme
            context.user_data['last_section'] = section_name
            return RESULT
    
    # Если тема не найдена
    themes = questionary.get_themes(section_name)
    reply_keyboard = [[theme] for theme in themes] + [["Назад", "Главное меню"]]
    
    await update.message.reply_text(
        "Пожалуйста, выбери одну из предложенных тем",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard)
    )
    return THEME

async def handle_result_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор после показа вопроса."""
    choice = update.message.text
    questionary: Questionary = context.bot_data['questionary']
    
    if choice == "Главное меню":
        return await start(update, context)
    elif choice == "Завершить":
        await update.message.reply_text(
            "Спасибо за ответы! До встречи! 👋\n/start",
            reply_markup=ReplyKeyboardRemove()
        )
        await end_dialog(context, 'completed')
        return ConversationHandler.END

    last_theme = context.user_data.get('last_theme')
    last_section = context.user_data.get('last_section')
    
    if choice == "Еще вопрос":
        if last_section and last_theme:
            question = questionary.get_random_question(last_section, last_theme)
            if question:
                await update.message.reply_text(
                    f"📖 {question}\n\n"
                    "Что хочешь сделать дальше?",
                    reply_markup=ReplyKeyboardMarkup(RESULT_MENU_KEYBOARD)
                )
                return RESULT
        
        # Если нет последней темы, возвращаем к выбору темы
        return await theme_choice(update, context, questionary)
    
    elif choice == "Выбрать другую тему":
        return await theme_choice(update, context, questionary)
    
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
    await end_dialog(context, 'cancelled')
    return ConversationHandler.END

async def end_dialog(context: ContextTypes.DEFAULT_TYPE, state: str = 'completed'):
    """Завершает диалог в базе данных."""
    try:
        if 'dialog_id' in context.user_data:
            await db.end_dialog(context.user_data['dialog_id'], state)
            logger.info(f"Dialog {context.user_data['dialog_id']} ended with state: {state}")
            # Удаляем ID диалога из контекста
            del context.user_data['dialog_id']
    except Exception as e:
        logger.error(f"Error ending dialog: {e}")
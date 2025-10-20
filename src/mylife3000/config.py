"""
Конфигурационный модуль бота.

Содержит настройки приложения, включая:
- Переменные окружения
- Состояния диалога (FSM)
- Клавиатуры и текстовые константы

Variables:
    BOT_TOKEN (str): Токен Telegram бота
    DATABASE_URL (str): URL подключения к PostgreSQL
    MAIN_MENU, SECTION_MENU, THEME, RESULT (int): Состояния конечного автомата
    *_KEYBOARD (List[List[str]]): Массивы кнопок для клавиатур
"""

import os
from typing import Dict
from dotenv import load_dotenv
import logging

# Загрузка переменных окружения
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Проверьте .env файл.")

# Настройки базы данных
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден! Проверьте .env файл.")

# Определяем состояния диалога
MAIN_MENU, SECTION_MENU, THEME, RESULT = range(4)

# Главное меню
MAIN_MENU_KEYBOARD = [
    ["Самопознание: Кто Я?"], 
    ["Вектор: Куда я движусь?", "Вызовы: Что мне мешает?"],
    ["Окружение: Мои отношения?", "Интеграция: Как я живу?"],
    ["Капсула Времени: История для моих детей"],
    ["О проекте"]
]

# Меню раздела
SECTION_MENU_KEYBOARD = [
    ["Случайный вопрос"],
    ["Выбрать тему"],
    ["Главное меню"]
]

# Меню результата
RESULT_MENU_KEYBOARD = [
    ["Еще вопрос"], 
    ["Выбрать другую тему"], 
    ["Главное меню", "Завершить"]
]
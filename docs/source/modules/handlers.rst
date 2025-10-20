Модуль обработчиков (handlers)
==============================

.. automodule:: mylife3000.handlers
   :members:
   :undoc-members:
   :show-inheritance:

Обзор
-----

Модуль ``handlers.py`` содержит все обработчики сообщений и команд Telegram бота,
реализующие логику диалога через конечный автомат состояний.

Архитектура обработчиков
------------------------

.. mermaid::

   stateDiagram-v2
       [*] --> MAIN_MENU: /start
       MAIN_MENU --> SECTION_MENU: Выбор раздела
       MAIN_MENU --> [*]: "О проекте"
       SECTION_MENU --> THEME: "Выбрать тему"
       SECTION_MENU --> MAIN_MENU: "Главное меню"
       SECTION_MENU --> [*]: "Случайный вопрос"
       THEME --> RESULT: Выбор темы
       THEME --> SECTION_MENU: "Назад"
       THEME --> MAIN_MENU: "Главное меню"
       RESULT --> RESULT: "Еще вопрос"
       RESULT --> THEME: "Выбрать другую тему"
       RESULT --> MAIN_MENU: "Главное меню"
       RESULT --> [*]: "Завершить"
       state MAIN_MENU {
           [*] --> start
           start --> handle_main_menu
       }
       state SECTION_MENU {
           [*] --> show_section_menu
           show_section_menu --> handle_section_choice
       }

Основные обработчики
--------------------

.. py:function:: start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int

   Начинает диалог и показывает главное меню.
   
   **Действия:**
   
   - Логирует начало диалога в БД
   - Сохраняет dialog_id в user_data
   - Показывает приветственное сообщение
   - Возвращает состояние MAIN_MENU

.. py:function:: handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int

   Обрабатывает выбор в главном меню.
   
   **Логика:**
   
   - При выборе раздела: сохраняет выбор и переходит к SECTION_MENU
   - При выборе "О проекте": завершает диалог
   - При неверном вводе: просит повторить выбор

.. py:function:: show_section_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, questionary: Questionary) -> int

   Показывает меню выбранного раздела с описанием.

.. py:function:: handle_section_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int

   Обрабатывает выбор в разделе.
   
   **Варианты:**
   
   - "Главное меню" - возврат к началу
   - "Случайный вопрос" - показывает случайный вопрос и завершает диалог
   - "Выбрать тему" - переход к выбору темы

.. py:function:: theme_choice(update: Update, context: ContextTypes.DEFAULT_TYPE, questionary: Questionary) -> int

   Предлагает выбор темы в текущем разделе.

.. py:function:: handle_theme_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int

   Обрабатывает выбор темы и показывает случайный вопрос.
   
   **Действия:**
   
   - Проверяет существование темы
   - Получает случайный вопрос через Questionary
   - Обновляет состояние диалога в БД
   - Показывает вопрос и переходит к RESULT

.. py:function:: handle_result_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int

   Обрабатывает действия после показа вопроса.
   
   **Варианты:**
   
   - "Еще вопрос" - показывает другой вопрос из той же темы
   - "Выбрать другую тему" - возврат к выбору темы
   - "Главное меню" - возврат к началу
   - "Завершить" - завершение диалога

.. py:function:: cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int

   Завершает диалог по команде /cancel.

Вспомогательные функции
-----------------------

.. py:function:: end_dialog(context: ContextTypes.DEFAULT_TYPE, state: str = 'completed')

   Завершает диалог в базе данных.
   
   **Parameters:**
   
   - ``context`` - контекст выполнения
   - ``state`` - состояние завершения

Flow данных
-----------

.. mermaid::

   flowchart TD
       A[Пользователь] --> B[Обработчик]
       B --> C[Questionary]
       B --> D[Database]
       C --> E[questions_data.py]
       D --> F[PostgreSQL]
       
       B --> G[Ответ пользователю]
       G --> A

Контекст user_data
------------------

Обработчики используют ``context.user_data`` для хранения:

+-----------------------+-----------------------------------------------+
| Ключ                  | Значение                                      |
+=======================+===============================================+
| ``dialog_id``         | ID текущего диалога в БД                     |
+-----------------------+-----------------------------------------------+
| ``current_section``   | Выбранный раздел                             |
+-----------------------+-----------------------------------------------+
| ``last_theme``        | Последняя выбранная тема                     |
+-----------------------+-----------------------------------------------+
| ``last_section``      | Последний выбранный раздел                   |
+-----------------------+-----------------------------------------------+

Обработка ошибок
----------------

Все обработчики включают блоки try-except для:

- Ошибок базы данных
- Ошибок получения вопросов
- Непредвиденных исключений

Ошибки логируются, но не прерывают работу бота.

Пример использования
--------------------

.. code-block:: python

   # В main.py
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

Смотрите также
--------------

* :doc:`main` - Регистрация обработчиков
* :doc:`questionary` - Получение вопросов
* :doc:`database` - Логирование диалогов
* :doc:`config` - Состояния и клавиатуры

Модуль базы данных (database)
=============================

.. automodule:: mylife3000.database
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Обзор
-----

Модуль ``database.py`` предоставляет:

* Асинхронное подключение к PostgreSQL через asyncpg
* Пул подключений для эффективного управления соединениями
* CRUD операции для таблицы диалогов
* Логирование операций с базой данных

Архитектура базы данных
-----------------------

.. mermaid::

   erDiagram
       DIALOGS {
           bigint id PK
           timestamp start_time
           timestamp end_time
           varchar dialog_state
       }

Класс Database
--------------

.. py:class:: Database()

   Основной класс для работы с базой данных.
   
   Атрибуты:
   
   .. py:attribute:: pool
      
      Пул подключений asyncpg.Pool (Optional)

Методы Database
---------------

.. py:method:: Database.init_pool()

   Инициализирует пул подключений к базе данных.
   
   **Raises:**
   
   - ``Exception`` - если подключение не удалось
   - ``RuntimeError`` - если таблицы не существуют

.. py:method:: Database.start_dialog() -> int

   Создает новую запись о начале диалога.
   
   **Returns:**
   
   - ``int`` - ID созданного диалога
   
   **Raises:**
   
   - ``RuntimeError`` - если пул не инициализирован

.. py:method:: Database.end_dialog(dialog_id: int, state: str = 'completed')

   Отмечает диалог как завершенный.
   
   **Parameters:**
   
   - ``dialog_id`` - ID диалога для завершения
   - ``state`` - Финальное состояние диалога
   
   **Raises:**
   
   - ``RuntimeError`` - если пул не инициализирован

.. py:method:: Database.update_dialog_state(dialog_id: int, state: str)

   Обновляет состояние диалога.
   
   **Parameters:**
   
   - ``dialog_id`` - ID диалога для обновления
   - ``state`` - Новое состояние диалога

.. py:method:: Database.close()

   Закрывает пул подключений.

Глобальный экземпляр
--------------------

.. py:data:: db

   Глобальный экземпляр класса Database для использования во всем приложении.

Схема таблицы dialogs
---------------------

.. code-block:: sql

   CREATE TABLE conversations.dialogs (
       id BIGSERIAL PRIMARY KEY,
       start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       end_time TIMESTAMP NULL,
       dialog_state VARCHAR(50) NOT NULL
   );

Состояния диалогов
------------------

+----------------------+-----------------------------------------------+
| Состояние            | Описание                                      |
+======================+===============================================+
| ``started``          | Диалог начат                                  |
+----------------------+-----------------------------------------------+
| ``section_<name>``   | Пользователь выбрал раздел                   |
+----------------------+-----------------------------------------------+
| ``theme_<name>``     | Пользователь выбрал тему                     |
+----------------------+-----------------------------------------------+
| ``random_question``  | Показан случайный вопрос                     |
+----------------------+-----------------------------------------------+
| ``completed``        | Диалог завершен нормально                    |
+----------------------+-----------------------------------------------+
| ``cancelled``        | Диалог отменен пользователем                |
+----------------------+-----------------------------------------------+
| ``project_info``     | Пользователь просмотрел информацию о проекте |
+----------------------+-----------------------------------------------+

Пример использования
--------------------

.. code-block:: python

   # Инициализация базы данных
   await db.init_pool()
   
   # Начало диалога
   dialog_id = await db.start_dialog()
   
   # Обновление состояния
   await db.update_dialog_state(dialog_id, "section_self_knowledge")
   
   # Завершение диалога
   await db.end_dialog(dialog_id, "completed")

Обработка ошибок
----------------

Все методы класса Database логируют ошибки и пробрасывают исключения:

- ``RuntimeError`` - при попытке использования неинициализированного пула
- ``asyncpg.PostgresError`` - при ошибках в запросах к базе данных

Смотрите также
--------------

* :doc:`handlers` - Использование базы данных в обработчиках
* :doc:`../installation` - Настройка PostgreSQL в Docker

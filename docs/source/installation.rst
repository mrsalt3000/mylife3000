Установка и запуск
==================

Предварительные требования
-------------------------

* Docker и Docker Compose
* Python 3.9+
* Telegram Bot Token

Клонирование и настройка
-----------------------

.. code-block:: bash

   git clone <repository-url>
   cd mylife3000
   cp docker/.env.example docker/.env

Настройка переменных окружения
-----------------------------

Отредактируйте ``docker/.env``:

.. code-block:: bash

   BOT_TOKEN=your_telegram_bot_token_here
   DATABASE_URL=postgresql://user:password@db:5432/mylife3000

Запуск в Docker
--------------

.. code-block:: bash

   cd docker
   docker-compose up -d

Локальная разработка
-------------------

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или venv\Scripts\activate  # Windows
   
   pip install -r requirements.txt
   python -m mylife3000
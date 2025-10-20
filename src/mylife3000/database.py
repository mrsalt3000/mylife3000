"""
Модуль для работы с базой данных.

Реализует паттерн Repository для абстракции доступа к данным.
Использует asyncpg для асинхронного подключения к PostgreSQL.

Classes:
    Database: Основной класс для управления подключением и операциями с БД

Attributes:
    db (Database): Глобальный экземпляр базы данных
"""

import asyncpg
import logging
from typing import Optional
from .config import DATABASE_URL

logger = logging.getLogger(__name__)

class Database:
    """
    Класс для управления подключением и операциями с базой данных.
    
    Использует пул подключений asyncpg для эффективного управления
    соединениями с PostgreSQL.
    
    Attributes:
        pool (Optional[asyncpg.Pool]): Пул подключений к БД
    """
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def init_pool(self):
        """
        Инициализирует пул подключений к базе данных.
        
        Raises
        ------
        Exception
            Если подключение не удалось или таблицы не существуют
        """

        try:
            self.pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool initialized")
            
            # Проверяем подключение к БД
            async with self.pool.acquire() as conn:
                # Простая проверка, что таблица существует
                await conn.fetchval('SELECT 1 FROM conversations.dialogs LIMIT 1')
                logger.info("Database tables verified")
                
        except Exception as e:
            logger.error(f"Error initializing database pool: {e}")
            logger.error("Make sure database is initialized via init.sql in Docker")
            raise

    async def start_dialog(self) -> int:
        """
        Создает новую запись о начале диалога.
        
        Returns
        -------
        int
            ID созданного диалога
            
        Raises
        ------
        RuntimeError
            Если пул подключений не инициализирован
        """

        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        async with self.pool.acquire() as conn:
            dialog_id = await conn.fetchval('''
                INSERT INTO conversations.dialogs (dialog_state) 
                VALUES ($1)
                RETURNING id
            ''', 'started')
            return dialog_id

    async def end_dialog(self, dialog_id: int, state: str = 'completed'):
        """
        Отмечает диалог как завершенный.
        
        Parameters
        ----------
        dialog_id : int
            ID диалога для завершения
        state : str, optional
            Финальное состояние диалога, по умолчанию 'completed'
            
        Raises
        ------
        RuntimeError
            Если пул подключений не инициализирован
        """

        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        async with self.pool.acquire() as conn:
            await conn.execute('''
                UPDATE conversations.dialogs 
                SET end_time = CURRENT_TIMESTAMP, dialog_state = $1
                WHERE id = $2
            ''', state, dialog_id)

    async def update_dialog_state(self, dialog_id: int, state: str):
        """
        Обновляет состояние диалога.
        
        Parameters
        ----------
        dialog_id : int
            ID диалога для обновления
        state : str
            Новое состояние диалога
            
        Raises
        ------
        RuntimeError
            Если пул подключений не инициализирован
        """
        
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        async with self.pool.acquire() as conn:
            await conn.execute('''
                UPDATE conversations.dialogs 
                SET dialog_state = $1
                WHERE id = $2
            ''', state, dialog_id)

    async def close(self):
        """Закрытие пула подключений"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

# Глобальный экземпляр базы данных
db = Database()
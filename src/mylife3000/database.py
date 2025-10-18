#!/usr/bin/env python

import asyncpg
import logging
from typing import Optional
from .config import DATABASE_URL

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def init_pool(self):
        """Инициализация пула подключений"""
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
        """Начало диалога и возврат ID записи"""
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
        """Завершение диалога"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        async with self.pool.acquire() as conn:
            await conn.execute('''
                UPDATE conversations.dialogs 
                SET end_time = CURRENT_TIMESTAMP, dialog_state = $1
                WHERE id = $2
            ''', state, dialog_id)

    async def update_dialog_state(self, dialog_id: int, state: str):
        """Обновление состояния диалога"""
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
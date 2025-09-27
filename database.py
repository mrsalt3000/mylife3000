#!/usr/bin/env python

import asyncpg
import logging
from typing import Optional
from config import DATABASE_URL

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
            
            # Проверяем существование таблицы
            async with self.pool.acquire() as conn:
                await self._create_tables(conn)
                
        except Exception as e:
            logger.error(f"Error initializing database pool: {e}")
            raise

    async def _create_tables(self, conn):
        """Создание таблиц если они не существуют"""
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS converstions.dialogs (
                id SERIAL PRIMARY KEY,
                start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP WITH TIME ZONE,
                dialog_state VARCHAR(50)
            )
        ''')
        logger.info("Database tables verified/created")

    async def start_dialog(self) -> int:
        """Начало диалога и возврат ID записи"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        async with self.pool.acquire() as conn:
            dialog_id = await conn.fetchval('''
                INSERT INTO converstions.dialogs (dialog_state) 
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
                UPDATE converstions.dialogs 
                SET end_time = CURRENT_TIMESTAMP, dialog_state = $1
                WHERE id = $2
            ''', state, dialog_id)

    async def update_dialog_state(self, dialog_id: int, state: str):
        """Обновление состояния диалога"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        async with self.pool.acquire() as conn:
            await conn.execute('''
                UPDATE converstions.dialogs 
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
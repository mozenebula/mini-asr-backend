# ==============================================================================
# Copyright (C) 2024 Evil0ctal
#
# This file is part of the Whisper-Speech-to-Text-API project.
# Github: https://github.com/Evil0ctal/Whisper-Speech-to-Text-API
#
# This project is licensed under the Apache License 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
#                                     ,
#              ,-.       _,---._ __  / \
#             /  )    .-'       `./ /   \
#            (  (   ,'            `/    /|
#             \  `-"             \'\   / |
#              `.              ,  \ \ /  |
#               /`.          ,'-`----Y   |
#              (            ;        |   '
#              |  ,-.    ,-'         |  /
#              |  | (   |  Evil0ctal | /
#              )  |  \  `.___________|/    Whisper API Out of the Box (Where is my ⭐?)
#              `--'   `--'
# ==============================================================================
#
# Contributor Link, Thanks for your contribution:
#
# No one yet...
#
# ==============================================================================

import traceback
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
from contextlib import asynccontextmanager
from app.database.models import Task, Base
from app.utils.logging_utils import configure_logging

# 配置日志记录器 | Configure logger
logger = configure_logging(name=__name__)


class DatabaseManager:
    _engine = None
    _session_factory = None

    @classmethod
    async def initialize(cls, database_url: str):
        """初始化数据库引擎和会话工厂 | Initialize database engine and session factory"""
        if not cls._engine:
            cls._engine = create_async_engine(database_url, echo=False)
            cls._session_factory = sessionmaker(
                bind=cls._engine,
                expire_on_commit=False,
                class_=AsyncSession
            )
            logger.info("Database engine and session factory initialized.")
            await cls.init_db()

    @classmethod
    async def init_db(cls):
        """初始化数据库表 | Initialize database tables"""
        try:
            async with cls._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully.")
        except SQLAlchemyError as e:
            logger.error(f"Error initializing database tables: {e}")
            logger.error(traceback.format_exc())
            raise

    @classmethod
    @asynccontextmanager
    async def get_session(cls) -> AsyncSession:
        """获取数据库会话生成器 | Get a database session generator"""
        async with cls._session_factory() as session:
            yield session

    async def get_task_by_id(self, task_id: int) -> Optional[dict]:
        """根据ID异步获取任务 | Asynchronously get task by ID"""
        async with self._session_factory() as session:
            try:
                task = await session.get(Task, task_id)
                return task.to_dict() if task else None
            except SQLAlchemyError as e:
                logger.error(f"Error fetching task by ID {task_id}: {e}")
                logger.error(traceback.format_exc())
                return None

    async def add_task(self, task: Task):
        """异步添加新任务 | Asynchronously add new task"""
        async with self._session_factory() as session:
            try:
                session.add(task)
                await session.commit()
            except SQLAlchemyError as e:
                logger.error(f"Error adding task: {e}")
                logger.error(traceback.format_exc())
                await session.rollback()

    async def update_task(self, task_id: int, **kwargs) -> Optional[dict]:
        """异步更新任务信息 | Asynchronously update task details"""
        async with self._session_factory() as session:
            try:
                task = await session.get(Task, task_id)
                if not task:
                    return None
                for key, value in kwargs.items():
                    setattr(task, key, value)
                await session.commit()
                return task.to_dict()
            except SQLAlchemyError as e:
                logger.error(f"Error updating task ID {task_id}: {e}")
                logger.error(traceback.format_exc())
                await session.rollback()
                return None

    async def delete_task(self, task_id: int) -> bool:
        """根据ID异步删除任务 | Asynchronously delete task by ID"""
        async with self._session_factory() as session:
            try:
                task = await session.get(Task, task_id)
                if task:
                    await session.delete(task)
                    await session.commit()
                    return True
                return False
            except SQLAlchemyError as e:
                logger.error(f"Error deleting task ID {task_id}: {e}")
                logger.error(traceback.format_exc())
                await session.rollback()
                return False

    async def get_all_tasks(self, limit: int = 100) -> List[dict]:
        """异步获取所有任务，支持限制返回数量 | Asynchronously get all tasks with a limit"""
        async with self._session_factory() as session:
            try:
                result = await session.execute(select(Task).limit(limit))
                tasks = result.scalars().all()
                return [task.to_dict() for task in tasks]
            except SQLAlchemyError as e:
                logger.error(f"Error fetching tasks: {e}")
                logger.error(traceback.format_exc())
                return []

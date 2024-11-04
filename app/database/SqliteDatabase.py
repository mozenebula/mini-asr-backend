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

import datetime
import traceback
from sqlalchemy import select, and_, func, case
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Dict, Union
from contextlib import asynccontextmanager
from app.database.models import Task, Base, QueryTasksOptionalFilter, TaskStatus, TaskPriority
from app.utils.logging_utils import configure_logging

# 配置日志记录器 | Configure logger
logger = configure_logging(name=__name__)


class SqliteDatabaseManager:
    _engine = None
    _session_factory = None

    @classmethod
    async def initialize(cls, database_url: str) -> None:
        """
        初始化数据库引擎和会话工厂

        Initialize database engine and session factory

        :param database_url: 数据库 URL | Database URL
        :return: None
        """
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
    async def init_db(cls) -> None:
        """
        初始化数据库表

        Initialize database tables

        :return: None
        """
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
        """
        获取数据库会话生成器

        Get a database session generator

        :return: 数据库会话 | Database session
        """
        async with cls._session_factory() as session:
            yield session

    async def get_task(self, task_id: int) -> Optional[Task]:
        """
        根据ID异步获取任务

        Asynchronously get task by ID

        :param task_id: 任务ID | Task ID
        :return: 任务信息 | Task details
        """
        async with self._session_factory() as session:
            try:
                task = await session.get(Task, task_id)
                return task if task else None
            except SQLAlchemyError as e:
                logger.error(f"Error fetching task by ID {task_id}: {e}")
                logger.error(traceback.format_exc())
                return None

    async def get_queued_tasks(self, max_concurrent_tasks: int) -> List[Task]:
        """
        异步获取队列中的任务

        Asynchronously get a task from the queue

        :param max_concurrent_tasks: 最大并发任务数 | Maximum number of concurrent tasks
        :return: 任务信息 | Task details
        """
        async with self._session_factory() as session:
            try:
                result = await session.execute(
                    select(Task)
                    .where(Task.status == TaskStatus.QUEUED)
                    .order_by(
                        case(
                            (Task.priority == TaskPriority.HIGH, 1),
                            (Task.priority == TaskPriority.NORMAL, 2),
                            (Task.priority == TaskPriority.LOW, 3),
                        )
                    )
                    .limit(max_concurrent_tasks)
                )
                remaining_tasks = result.scalars().all()
                return remaining_tasks
            except SQLAlchemyError as e:
                logger.error(f"Error fetching queued task: {e}")
                logger.error(traceback.format_exc())
                raise

    async def add_task(self, task: Task) -> None:
        """
        异步添加新任务

        Asynchronously add new task

        :param task: Task 对象 | Task object
        :return: None
        """
        async with self._session_factory() as session:
            try:
                session.add(task)
                await session.commit()
            except SQLAlchemyError as e:
                logger.error(f"Error adding task: {e}")
                logger.error(traceback.format_exc())
                await session.rollback()

    async def update_task(self, task_id: int, **kwargs) -> Optional[dict]:
        """
        异步更新任务信息

        Asynchronously update task details

        :param task_id: 任务ID | Task ID
        :param kwargs: 需要更新的字段 | Fields to update
        :return: 更新后的任务信息 | Updated task details
        """
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
        """
        根据ID异步删除任务

        Asynchronously delete task by ID

        :param task_id: 任务ID | Task ID
        :return: 是否删除成功 | Whether the deletion was successful
        """
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
        """
        异步获取所有任务，支持限制返回数量

        Asynchronously get all tasks with a limit

        :param limit: 返回数量限制 | Limit of returned tasks
        :return: 任务列表 | List of tasks
        """
        async with self._session_factory() as session:
            try:
                result = await session.execute(select(Task).limit(limit))
                tasks = result.scalars().all()
                return [task.to_dict() for task in tasks]
            except SQLAlchemyError as e:
                logger.error(f"Error fetching tasks: {e}")
                logger.error(traceback.format_exc())
                return []

    async def query_tasks(self, filters: QueryTasksOptionalFilter) -> Optional[Dict[str, List[Dict]]]:
        """
        按条件查询任务，使用分页和条件查询

        Query tasks with pagination and conditions.

        :param filters: QueryTasksOptionalFilter 对象 | QueryTasksOptionalFilter object
        :return: 查询结果 | Query result
        """
        async with self._session_factory() as session:
            try:
                # 构建查询条件 | Build query conditions
                conditions = self._build_query_conditions(filters)

                # 构建查询语句 | Build query statement
                query = (
                    select(Task)
                    .where(and_(*conditions))
                    .order_by(Task.created_at)
                    .offset(filters.offset)
                    .limit(filters.limit)
                )

                result = await session.execute(query)
                tasks = result.scalars().all()

                # 获取总记录数 | Get total count
                count_query = select(func.count()).select_from(Task).where(and_(*conditions))
                total_count = (await session.execute(count_query)).scalar()

                # 计算是否有更多数据，并返回 next_offset 以供下一页查询 | Calculate if there are more data and return next_offset for next page query
                has_more = filters.offset + filters.limit < total_count
                next_offset = filters.offset + filters.limit if has_more else None

                return {
                    "tasks": [task.to_dict() for task in tasks],
                    "total_count": total_count,
                    "has_more": has_more,
                    "next_offset": next_offset
                }

            except SQLAlchemyError as e:
                logger.error(f"Error querying tasks: {e}")
                logger.error(traceback.format_exc())
                raise

    def _build_query_conditions(self, filters: QueryTasksOptionalFilter) -> List:
        """
        根据 QueryTasksOptionalFilter 对象构建查询条件

        Build query conditions based on QueryTasksOptionalFilter.

        :param filters: QueryTasksOptionalFilter 对象 | QueryTasksOptionalFilter object
        :return: 查询条件列表 | List of query conditions
        """
        conditions = []
        if filters.status:
            conditions.append(Task.status == filters.status)
        if filters.priority:
            conditions.append(Task.priority == filters.priority)
        if filters.created_after:
            conditions.append(Task.created_at >= filters.created_after)
        if filters.created_before:
            conditions.append(Task.created_at <= filters.created_before)
        if filters.language:
            conditions.append(Task.language == filters.language)
        if filters.engine_name:
            conditions.append(Task.engine_name == filters.engine_name)
        if filters.has_result is not None:
            conditions.append((Task.result != None) if filters.has_result else (Task.result == None))
        if filters.has_error is not None:
            conditions.append((Task.error_message != None) if filters.has_error else (Task.error_message == None))
        return conditions

    async def update_task_callback_status(self, task_id: int,
                                          callback_status_code: int,
                                          callback_message: Optional[str],
                                          callback_time: Union[str, datetime.datetime]
                                          ) -> None:
        """
        更新任务的回调状态码、回调消息和回调时间

        Update the task's callback status code, callback message, and callback time

        :param task_id: 任务ID | Task ID
        :param callback_status_code: 回调状态码 | Callback status code
        :param callback_message: 回调消息 | Callback message
        :param callback_time: 回调时间 | Callback time
        :return: None
        """
        async with self._session_factory() as session:
            try:
                task = await session.get(Task, task_id)
                if task:
                    task.callback_status_code = callback_status_code
                    task.callback_message = callback_message
                    task.callback_time = callback_time
                    await session.commit()
                    logger.info(f"Task callback status updated for task ID {task_id}, status code: {callback_status_code}")
                    # logger.debug(f"Task Dtail: {task.to_dict()}")
            except SQLAlchemyError as e:
                logger.error(f"Error updating task callback status for task ID {task_id}: {e}")
                logger.error(traceback.format_exc())
                await session.rollback()
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

import asyncio
import datetime
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import List

from sqlalchemy import select, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import DatabaseManager
from app.database.models import Task, TaskStatus, TaskPriority
from app.model_pool.async_model_pool import AsyncModelPool
from app.utils.file_utils import FileUtils
from app.utils.logging_utils import configure_logging
from config.settings import Settings

# 任务并发数 | Task concurrency
max_concurrent_tasks: int = Settings.WhisperSettings.MAX_CONCURRENT_TASKS

# 初始化静态线程池，所有实例共享 | Initialize static thread pool, shared by all instances
_executor: ThreadPoolExecutor = ThreadPoolExecutor()


class TaskProcessor:
    """
    任务处理器类，用于从数据库中获取任务并在后台处理任务。

    Task processor class for fetching tasks from the database and processing them in the background.
    """

    def __init__(self,
                 model_pool: AsyncModelPool,
                 file_utils: FileUtils,
                 db_manager: DatabaseManager) -> None:
        """
        初始化 TaskProcessor 实例，设置模型、文件工具和数据库管理器。

        Initializes the TaskProcessor instance with the model pool, file utilities, and database manager.

        :param model_pool: AsyncModelPool 实例，用于模型管理 | AsyncModelPool instance for model management
        :param file_utils: FileUtils 实例，用于文件操作 | FileUtils instance for file operations
        :param db_manager: DatabaseManager 实例，用于数据库交互 | DatabaseManager instance for database interactions
        :return: None
        """
        self.model_pool: AsyncModelPool = model_pool
        self.file_utils: FileUtils = file_utils
        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.thread: threading.Thread = threading.Thread(target=self.run_loop)
        self.logger = configure_logging(name=__name__)
        self.shutdown_event: threading.Event = threading.Event()
        self.db_manager: DatabaseManager = db_manager
        self.task_status_check_interval: int = Settings.WhisperSettings.TASK_STATUS_CHECK_INTERVAL

    def start(self) -> None:
        """
        启动任务处理器的后台线程和事件循环。

        Starts the background thread and event loop for task processing.

        :return: None
        """
        self.thread.start()
        self.logger.info("TaskProcessor started.")

    def stop(self) -> None:
        """
        停止任务处理器的后台线程和事件循环，确保所有任务完成。

        Stops the background thread and event loop of the task processor, ensuring all tasks are completed.

        :return: None
        """
        self.shutdown_event.set()
        # 以线程安全的方式停止事件循环 | Stop the event loop in a thread-safe manner
        self.loop.call_soon_threadsafe(self.loop.stop)
        # 等待线程结束 | Wait for the thread to finish
        self.thread.join()
        self.logger.info("TaskProcessor stopped.")

    def run_loop(self) -> None:
        """
        在后台运行异步事件循环以处理任务队列，直到停止信号触发。

        Runs the asynchronous event loop in the background to process the task queue until a stop signal is triggered.
        """
        asyncio.set_event_loop(self.loop)

        # 使用 create_task 启动 process_tasks 作为持续运行的后台任务 | Start process_tasks as a continuous background task using create_task
        self.loop.create_task(self.process_tasks())

        # 使用 run_forever 让事件循环一直运行，直到 stop 被调用 | Use run_forever to keep the event loop running until stop is called
        self.loop.run_forever()

        # 在退出前清理事件循环中的挂起任务 | Clean up pending tasks in the event loop before exiting
        pending = asyncio.all_tasks(self.loop)
        if pending:
            self.loop.run_until_complete(asyncio.gather(*pending))

        self.loop.close()
        self.logger.info("TaskProcessor Event loop closed.")

    async def process_tasks(self) -> None:
        """
        持续从数据库中按优先级拉取任务并处理。若无任务，则等待并重试。

        Continuously fetches tasks from the database by priority and processes them. Waits and retries if no tasks are available.

        :return: None
        """
        # 记录上次日志输出的时间 | Record the time of the last log output
        last_log_time = 0
        # 日志输出间隔，单位为秒 | Log output interval in seconds
        log_delay = 30

        while not self.shutdown_event.is_set():
            try:
                async with self.db_manager.get_session() as session:
                    tasks: List[Task] = await self._fetch_multiple_tasks(session, limit=max_concurrent_tasks)

                    if tasks:
                        await self._process_multiple_tasks(tasks)
                    else:
                        current_time = time.time()
                        if current_time - last_log_time >= log_delay:
                            self.logger.info(f"No tasks to process, waiting for new tasks...")
                            last_log_time = current_time
                        await asyncio.sleep(self.task_status_check_interval)
            except Exception as e:
                self.logger.error(f"Error while pulling tasks from the database: {str(e)}")
                self.logger.error(traceback.format_exc())
                await asyncio.sleep(self.task_status_check_interval)

    async def _fetch_multiple_tasks(self, session: AsyncSession, limit: int = 1) -> List[Task]:
        """
        从数据库中按优先级获取指定数量的排队任务。

        Fetches a specified number of queued tasks from the database based on priority.

        :param session: 当前的数据库会话，用于执行查询 | The current database session for executing the query
        :param limit: 要获取的任务数限制 | The limit on the number of tasks to fetch
        :return: 按优先级排序的任务列表 | List of tasks sorted by priority
        """
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
            .limit(limit)
        )
        remaining_tasks = result.scalars().all()
        return remaining_tasks

    async def _process_multiple_tasks(self, tasks: List[Task]) -> None:
        """
        并行处理给定的多个任务，将每个任务提交到线程池。

        Processes multiple tasks in parallel, submitting each to the thread pool.

        :param tasks: 要处理的任务列表 | List of tasks to process
        :return: None
        """
        loop = asyncio.get_running_loop()
        futures = [
            loop.run_in_executor(_executor, self._process_task_sync, task)
            for task in tasks
        ]

        # 使用 gather 并设置 return_exceptions=True 以便即使某个任务失败也不会影响其他任务
        # Use gather with return_exceptions=True to allow all tasks to complete even if some fail
        results = await asyncio.gather(*futures, return_exceptions=True)

        for task, result in zip(tasks, results):
            if isinstance(result, Exception):
                self.logger.error(
                    f"""
                    Error processing task:
                    ID          : {task.id}
                    Priority    : {task.priority}
                    File        : {task.file_name}
                    Size        : {task.file_size_bytes} bytes
                    Duration    : {task.duration:.2f} seconds
                    Created At  : {task.created_at}
                    Output URL  : {task.output_url}
                    Error       : {str(result)}
                    """,
                    exc_info=result
                )
            else:
                self.logger.info(f"Task {task.id} processed successfully.")

    def _process_task_sync(self, task: Task) -> None:
        """
        在线程池中同步处理单个任务，包括音频转录和数据库更新。

        Synchronously processes a single task in the thread pool, including audio transcription and database updates.

        :param task: 要处理的任务实例 | The task instance to process
        :return: None
        """
        try:
            self.logger.info(
                f"""
                Processing queued task:
                ID          : {task.id}
                Priority    : {task.priority}
                File        : {task.file_name}
                Size        : {task.file_size_bytes} bytes
                Duration    : {task.duration:.2f} seconds
                Created At  : {task.created_at}
                Output URL  : {task.output_url}
                """
            )

            # 获取模型实例 | Acquire a model instance
            model = asyncio.run(self.model_pool.get_model())

            try:
                # 记录任务开始时间 | Record task start time
                task_start_time: datetime.datetime = datetime.datetime.utcnow()

                # 执行转录任务 | Perform transcription task
                result = model.transcribe(task.file_path, **task.decode_options or {})

                # 更新任务状态和结果 | Update task status and result
                task_update = {
                    "status": TaskStatus.COMPLETED,
                    "language": result.get('language'),
                    "result": result,
                    "total_time": (datetime.datetime.utcnow() - task_start_time).total_seconds()
                }
                asyncio.run(self.db_manager.update_task(task.id, **task_update))

            finally:
                # 将模型实例归还到池中 | Return the model instance to the pool
                asyncio.run(self.model_pool.return_model(model))

        except Exception as e:
            task_update = {
                "status": TaskStatus.FAILED,
                "error_message": str(e)
            }
            asyncio.run(self.db_manager.update_task(task.id, **task_update))
            self.logger.error(
                f"""
                Error processing tasks: 
                ID          : {task.id}
                Priority    : {task.priority}
                File        : {task.file_name}
                Size        : {task.file_size_bytes} bytes
                Duration    : {task.duration:.2f} seconds
                Created At  : {task.created_at}
                Output URL  : {task.output_url}
                Error       : {str(e)}
                """
            )
            self.logger.error(traceback.format_exc())
        finally:
            # 删除临时文件 | Delete temporary file
            if Settings.FileSettings.delete_temp_files_after_processing:
                asyncio.run(self.file_utils.delete_file(task.file_path))
            else:
                self.logger.debug(f"Keeping temporary file: {task.file_path}")

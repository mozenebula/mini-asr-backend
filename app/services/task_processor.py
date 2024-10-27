import asyncio
import threading

import whisper
from sqlalchemy import select

from app.database.database import DatabaseManager
from app.database.models import Task, TaskStatus
from app.utils.file_utils import FileUtils
from app.utils.logging_utils import configure_logging
from config.settings import Settings


class TaskProcessor:
    """
    任务处理器，用于后台处理任务队列

    Task processor for handling tasks in the background.
    """

    def __init__(self,
                 model: whisper.Whisper,
                 file_utils: FileUtils,
                 db_manager: DatabaseManager) -> None:
        """
        :param model: Whisper 模型实例 | Whisper model instance
        :param file_utils: FileUtils 实例 | FileUtils instance
        :param db_manager: DatabaseManager 实例 | DatabaseManager instance
        :return: None
        """
        self.model = model
        self.file_utils = file_utils
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_loop, daemon=True)
        self.logger = configure_logging(name=__name__)
        self.shutdown_event = threading.Event()
        self.db_manager = db_manager

    def start(self):
        """启动任务处理器 | Start the task processor"""
        self.thread.start()
        self.logger.info("TaskProcessor started.")

    def stop(self):
        """停止任务处理器 | Stop the task processor"""
        self.shutdown_event.set()
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()
        self.logger.info("TaskProcessor stopped.")

    def run_loop(self):
        """运行异步事件循环 | Run the asynchronous event loop"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.process_tasks())

    async def process_tasks(self):
        while not self.shutdown_event.is_set():
            try:
                async with self.db_manager.get_session() as session:
                    # 从数据库中获取一个待处理的任务 | Get a task to process from the database
                    result = await session.execute(
                        select(Task).where(Task.status == TaskStatus.QUEUED).limit(1)
                    )
                    task = result.scalar_one_or_none()

                    # 如果有任务，则将其状态设置为处理中并提交 | If there is a task, set its status to processing and commit
                    if task:
                        task.status = TaskStatus.PROCESSING
                        await session.commit()
                        # 处理任务 | Process task
                        await self.process_task(task)
                    else:
                        await asyncio.sleep(5)
            except Exception as e:
                self.logger.error(f"Error in processing tasks: {str(e)}")
                await asyncio.sleep(5)

    async def process_task(self, task):
        try:
            self.logger.info(f"Processing task {task.id}")
            # 执行转录任务 | Perform transcription task
            result = self.model.transcribe(task.file_path, **(task.decode_options or {}))

            # 更新任务状态和结果 | Update task status and result
            async with self.db_manager.get_session() as session:
                task_in_db = await session.get(Task, task.id)
                task_in_db.status = TaskStatus.COMPLETED
                task_in_db.result = result
                await session.commit()

            # 删除临时文件 | Delete temporary file
            if Settings.FileSettings.delete_temp_files_after_processing:
                await self.file_utils.delete_file(task.file_path)
            else:
                self.logger.debug(f"Keeping temporary file: {task.file_path}")

        except Exception as e:
            async with self.db_manager.get_session() as session:
                task_in_db = await session.get(Task, task.id)
                task_in_db.status = TaskStatus.FAILED
                task_in_db.error_message = str(e)
                await session.commit()

            self.logger.error(f"Failed to process task {task.id}: {str(e)}")

            # 删除临时文件 | Delete temporary file
            if Settings.FileSettings.delete_temp_files_after_processing:
                await self.file_utils.delete_file(task.file_path)
            else:
                self.logger.debug(f"Keeping temporary file: {task.file_path}")

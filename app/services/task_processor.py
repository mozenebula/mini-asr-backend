import asyncio
import threading
import whisper
import datetime

from sqlalchemy import select, case
from app.database.database import DatabaseManager
from app.database.models import Task, TaskStatus, TaskPriority

from app.utils.file_utils import FileUtils
from app.utils.logging_utils import configure_logging

from concurrent.futures import ThreadPoolExecutor
from config.settings import Settings


class TaskProcessor:
    """
    任务处理器，用于后台处理任务队列

    Task processor for handling tasks in the background.
    """

    # 初始化静态线程池，所有实例共享 | Initialize static thread pool, shared by all instances
    _executor = ThreadPoolExecutor(max_workers=5)

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
                    # 按优先级从高到低从数据库中获取一个待处理的任务 | Get a task to process from the database by priority from high to low
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
                        .limit(1)
                    )
                    task = result.scalar_one_or_none()

                    # 如果有任务，则将其状态设置为处理中并提交 | If there is a task, set its status to processing and commit
                    if task:
                        task.status = TaskStatus.PROCESSING
                        await session.commit()
                        # 处理任务 | Process task
                        await self.process_task(task)
                    else:
                        # 如果没有任务，则等待 1 秒 | If there is no task, wait for 1 second
                        self.logger.debug("No tasks to process. Waiting...")
                        await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Error while pulling tasks from the database: {str(e)}")
                await asyncio.sleep(1)

    async def process_task(self, task):

        # 辅助函数来包装 transcribe 调用
        def transcribe_with_options(model, file_path, options):
            return model.transcribe(file_path, **options)

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

            # 记录任务开始时间 | Record task start time
            task_start_time = datetime.datetime.utcnow()

            # 执行转录任务 | Perform transcription task
            result = await asyncio.get_running_loop().run_in_executor(
                TaskProcessor._executor, transcribe_with_options, self.model, task.file_path, task.decode_options or {}
            )

            # 更新任务状态和结果 | Update task status and result
            async with self.db_manager.get_session() as session:
                task_in_db = await session.get(Task, task.id)
                # 更新任务状态为已完成 | Update task status to completed
                task_in_db.status = TaskStatus.COMPLETED
                # 更新任务语言 | Update task language
                task_in_db.language = result.get('language')
                # 更新任务结果 | Update task result
                task_in_db.result = result
                # 更新任务总耗时 | Update total time
                task_in_db.total_time = (datetime.datetime.utcnow() - task_start_time).total_seconds()
                await session.commit()

            # 删除临时文件 | Delete temporary file
            if Settings.FileSettings.delete_temp_files_after_processing:
                await self.file_utils.delete_file(task.file_path)
            else:
                self.logger.debug(f"Keeping temporary file: {task.file_path}")

        except Exception as e:
            async with self.db_manager.get_session() as session:
                task_in_db = await session.get(Task, task.id)
                # 更新任务状态为失败 | Update task status to failed
                task_in_db.status = TaskStatus.FAILED
                # 更新错误信息 | Update error message
                task_in_db.error_message = str(e)
                await session.commit()

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

            # 删除临时文件 | Delete temporary file
            if Settings.FileSettings.delete_temp_files_after_processing:
                await self.file_utils.delete_file(task.file_path)
            else:
                self.logger.debug(f"Keeping temporary file: {task.file_path}")

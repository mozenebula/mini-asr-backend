import asyncio
import threading
import traceback
import whisper
import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case
from app.database.database import DatabaseManager
from app.database.models import Task, TaskStatus, TaskPriority
from app.utils.file_utils import FileUtils
from app.utils.logging_utils import configure_logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from config.settings import Settings

# 任务并发数 | Task concurrency
max_concurrent_tasks: int = Settings.WhisperSettings.MAX_CONCURRENT_TASKS

# TODO: 2024-10-28-Evil0ctal: 请查看下方的注释 | Please see the comments below
"""
[中文]
当前代码中使用了 ThreadPoolExecutor 作为静态线程池，用于处理任务。
ThreadPoolExecutor由于 GIL，在使用CPU进行任务处理时可能无法提供所需的并发性。
在这种情况下，可以考虑使用 ProcessPoolExecutor 作为替代方案，以便在多核CPU上实现更好的并发性。
但是如果是使用GPU进行任务处理，ThreadPoolExecutor 仍然是一个不错的选择。
如果你有更好的建议，欢迎提出一个Issue或者Pull Request。

[English]
The current code uses ThreadPoolExecutor as a static thread pool for task processing.
ThreadPoolExecutor may not provide the desired concurrency when using CPU for task processing due to the GIL.
In such cases, consider using ProcessPoolExecutor as an alternative for better concurrency on multi-core CPUs.
However, ThreadPoolExecutor is still a good choice if using a GPU for task processing.
If you have better suggestions, feel free to raise an Issue or Pull Request.
"""
# 初始化静态线程池，所有实例共享 | Initialize static thread pool, shared by all instances
_executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=max_concurrent_tasks)


class TaskProcessor:
    """
    任务处理器类，用于从数据库中获取任务并在后台处理任务。

    Task processor class for fetching tasks from the database and processing them in the background.
    """

    def __init__(self,
                 model: whisper.Whisper,
                 file_utils: FileUtils,
                 db_manager: DatabaseManager) -> None:
        """
        初始化 TaskProcessor 实例，设置模型、文件工具和数据库管理器。

        Initializes the TaskProcessor instance with the model, file utilities, and database manager.

        :param model: Whisper 模型实例，用于音频转录 | Whisper model instance for audio transcription
        :param file_utils: FileUtils 实例，用于文件操作 | FileUtils instance for file operations
        :param db_manager: DatabaseManager 实例，用于数据库交互 | DatabaseManager instance for database interactions
        :return: None
        """
        self.model: whisper.Whisper = model
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
        while not self.shutdown_event.is_set():
            try:
                async with self.db_manager.get_session() as session:
                    tasks: List[Task] = await self._fetch_multiple_tasks(session, limit=max_concurrent_tasks)

                    if tasks:
                        await self._process_multiple_tasks(tasks)
                    else:
                        self.logger.info(f"No tasks to process, waiting for {self.task_status_check_interval} seconds.")
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
        return result.scalars().all()

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
                    Traceback   : {result.__traceback__}
                    """
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

        def transcribe_with_options(model: whisper.Whisper, file_path: str, options: Optional[dict]) -> dict:
            """
            执行模型的转录操作。

            Performs the transcription operation using the model.

            :param model: Whisper 模型实例 | Whisper model instance
            :param file_path: 音频文件路径 | File path of the audio
            :param options: 转录选项字典 | Dictionary of transcription options
            :return: 转录结果字典 | Dictionary containing the transcription result
            """
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
            task_start_time: datetime.datetime = datetime.datetime.utcnow()

            # 执行转录任务 | Perform transcription task
            result = transcribe_with_options(self.model, task.file_path, task.decode_options or {})

            # 更新任务状态和结果 | Update task status and result
            task_update = {
                "status": TaskStatus.COMPLETED,
                "language": result.get('language'),
                "result": result,
                "total_time": (datetime.datetime.utcnow() - task_start_time).total_seconds()
            }
            asyncio.run(self.db_manager.update_task(task.id, **task_update))

        except Exception as e:
            # 更新任务状态为 FAILED，并提交更改 | Mark task as FAILED and submit changes
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

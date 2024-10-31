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

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.router import router as api_router
from app.database.database import DatabaseManager
from app.model_pool.async_model_pool import AsyncModelPool
from app.services.whisper_service import WhisperService
from app.utils.logging_utils import configure_logging
from config.settings import Settings

# 配置日志记录器 | Configure the logger
logger = configure_logging(name=__name__)

# API Tags
tags_metadata = [
    {
        "name": "Health-Check",
        "description": "**(服务器健康检查/Server Health Check)**",
    },
    {
        "name": "Whisper-Tasks",
        "description": "**(Whisper 任务/Whisper Tasks)**",
    },
]


@asynccontextmanager
async def lifespan(application: FastAPI):
    """
    FastAPI 生命周期上下文管理器 | FastAPI Lifecycle context manager
    :param application: FastAPI 应用实例 | FastAPI application instance
    :return: None
    """
    # 检查是否使用了 'faster_whisper' 引擎，并且 'MAX_CONCURRENT_TASKS' 设置大于 1
    # 如果是，则强制将 'MAX_CONCURRENT_TASKS' 设置为 1，这将有助于避免性能问题
    # Check if 'faster_whisper' engine is used and 'MAX_CONCURRENT_TASKS' setting is greater than 1
    # If so, force 'MAX_CONCURRENT_TASKS' to 1, this will help to avoid performance issues
    if Settings.AsyncModelPoolSettings.engine == "faster_whisper" and Settings.WhisperServiceSettings.MAX_CONCURRENT_TASKS > 1:
        logger.warning(f"""
            Detected 'faster_whisper' engine with 'MAX_CONCURRENT_TASKS' had been set to {Settings.WhisperServiceSettings.MAX_CONCURRENT_TASKS}.
            Will force 'MAX_CONCURRENT_TASKS' to 1 for 'faster_whisper' engine, this will help to avoid performance issues.
            """)
        Settings.WhisperServiceSettings.MAX_CONCURRENT_TASKS = 1

    # 初始化数据库 | Initialize the database
    db_manager = DatabaseManager()
    await db_manager.initialize(Settings.DatabaseSettings.url)

    # 实例化异步模型池 | Instantiate the asynchronous model pool
    model_pool = AsyncModelPool(
        # 模型池设置 | Model Pool Settings
        engine=Settings.AsyncModelPoolSettings.engine,
        min_size=Settings.AsyncModelPoolSettings.min_size,
        max_size=Settings.AsyncModelPoolSettings.get_max_size(),
        create_with_max_concurrent_tasks=Settings.AsyncModelPoolSettings.create_with_max_concurrent_tasks(),

        # openai_whisper 引擎设置 | openai_whisper Engine Settings
        openai_whisper_model_name=Settings.OpenAIWhisperSettings.openai_whisper_model_name,
        openai_whisper_device=Settings.OpenAIWhisperSettings.openai_whisper_device,
        openai_whisper_download_root=Settings.OpenAIWhisperSettings.openai_whisper_download_root,
        openai_whisper_in_memory=Settings.OpenAIWhisperSettings.openai_whisper_in_memory,

        # faster_whisper 引擎设置 | faster_whisper Engine Settings
        faster_whisper_model_size_or_path=Settings.FasterWhisperSettings.faster_whisper_model_size_or_path,
        faster_whisper_device=Settings.FasterWhisperSettings.faster_whisper_device,
        faster_whisper_device_index=Settings.FasterWhisperSettings.faster_whisper_device_index,
        faster_whisper_compute_type=Settings.FasterWhisperSettings.faster_whisper_compute_type,
        faster_whisper_cpu_threads=Settings.FasterWhisperSettings.faster_whisper_cpu_threads,
        faster_whisper_num_workers=Settings.FasterWhisperSettings.faster_whisper_num_workers,
        faster_whisper_download_root=Settings.FasterWhisperSettings.faster_whisper_download_root
    )
    # 初始化模型池，加载模型，这可能需要一些时间 | Initialize the model pool, load the model, this may take some time
    await model_pool.initialize_pool()

    # 实例化 WhisperService | Instantiate WhisperService
    whisper_service = WhisperService(
        model_pool=model_pool,
        db_manager=db_manager,
        max_concurrent_tasks=Settings.WhisperServiceSettings.MAX_CONCURRENT_TASKS,
        task_status_check_interval=Settings.WhisperServiceSettings.TASK_STATUS_CHECK_INTERVAL,
    )

    # 启动任务处理器 | Start the task processor
    whisper_service.start_task_processor()

    # 将数据库管理器存储在应用的 state 中 | Store db_manager in the app state
    application.state.db_manager = db_manager

    # 将 whisper_service 存储在应用的 state 中 | Store whisper_service in the app state
    application.state.whisper_service = whisper_service

    # 等待生命周期完成 | Wait for the lifecycle to complete
    yield

    # 停止任务处理器 | Stop the task processor
    whisper_service.stop_task_processor()


# 创建 FastAPI 应用实例
app = FastAPI(
    title=Settings.FastAPISettings.title,
    description=Settings.FastAPISettings.description,
    version=Settings.FastAPISettings.version,
    openapi_tags=tags_metadata,
    docs_url=Settings.FastAPISettings.docs_url,
    debug=Settings.FastAPISettings.debug,
    lifespan=lifespan
)

# API 路由 | API Router
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=Settings.FastAPISettings.ip, port=Settings.FastAPISettings.port)

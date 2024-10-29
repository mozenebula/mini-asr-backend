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
from config.settings import Settings


@asynccontextmanager
async def lifespan(application: FastAPI):
    """
    FastAPI 生命周期上下文管理器 | FastAPI Lifecycle context manager
    :param application: FastAPI 应用实例 | FastAPI application instance
    :return: None
    """

    # 初始化数据库 | Initialize the database
    await DatabaseManager.initialize(Settings.DatabaseSettings.url)

    # 实例化异步模型池 | Instantiate the asynchronous model pool
    async_model_pool = AsyncModelPool(
        model_name=Settings.WhisperSettings.model_name,
        device=Settings.WhisperSettings.device,
        download_root=Settings.WhisperSettings.download_root,
        in_memory=Settings.WhisperSettings.in_memory,
        min_size=Settings.AsyncModelPoolSettings.min_size,
        max_size=Settings.AsyncModelPoolSettings.get_max_size(),
        create_with_max_concurrent_tasks=Settings.AsyncModelPoolSettings.create_with_max_concurrent_tasks()
    )
    # 初始化模型池，加载模型，这可能需要一些时间 | Initialize the model pool, load the model, this may take some time
    await async_model_pool.initialize_pool()

    # 实例化 WhisperService | Instantiate WhisperService
    whisper_service = WhisperService(model_pool=async_model_pool)

    # 启动任务处理器 | Start the task processor
    whisper_service.start_task_processor()

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
    docs_url=Settings.FastAPISettings.docs_url,
    debug=Settings.FastAPISettings.debug,
    lifespan=lifespan
)

# API Tags
tags_metadata = [
    {
        "name": "Health-Check",
        "description": "**(服务器健康检查/Server Health Check)**",
    },
    {
        "name": "Whisper-Transcribe",
        "description": "**(Whisper语音转文本/Whisper Speech to Text)**",
    },
]

# API 路由 | API Router
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=Settings.FastAPISettings.ip, port=Settings.FastAPISettings.port)

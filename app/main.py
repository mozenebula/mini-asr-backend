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

from fastapi import FastAPI
from app.api.router import router as api_router
from app.database.database import DatabaseManager
from app.services.whisper_service_instance import whisper_service
from config.settings import Settings

# 创建 FastAPI 应用实例
app = FastAPI(
    title=Settings.FastAPISettings.title,
    description=Settings.FastAPISettings.description,
    version=Settings.FastAPISettings.version,
    docs_url=Settings.FastAPISettings.docs_url,
    debug=Settings.FastAPISettings.debug
)

# 数据库地址 | Database URL
DATABASE_URL = Settings.DatabaseSettings.url

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

@app.on_event("startup")
async def startup_event():
    # 初始化数据库 | Initialize the database
    await DatabaseManager.initialize(DATABASE_URL)
    # 启动任务处理器 | Start the task processor
    whisper_service.start_task_processor()

@app.on_event("shutdown")
async def shutdown_event():
    # 停止任务处理器 | Stop the task processor
    whisper_service.stop_task_processor()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Settings.FastAPISettings.ip, port=Settings.FastAPISettings.port)


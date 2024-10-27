from fastapi import FastAPI
from app.api import transcribe, health_check
from app.database.database import DatabaseManager
from app.services.whisper_service_instance import whisper_service

# 创建 FastAPI 应用实例
app = FastAPI(
    title="Whisper Speech to Text API",
    description="An open source Speech-to-Text API. The project is based on OpenAI's Whisper model and uses the asynchronous features of FastAPI to efficiently wrap it and support more custom functions.",
    version="1.0.0",
    docs_url="/",
)

# 数据库地址 | Database URL
DATABASE_URL = 'sqlite+aiosqlite:///tasks.db'

# 包含健康检查和音频转录的路由
app.include_router(health_check.router, prefix="/health", tags=["Health Check"])
app.include_router(transcribe.router, prefix="/transcribe", tags=["Transcribe"])

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
    uvicorn.run(app, host="0.0.0.0", port=8000)


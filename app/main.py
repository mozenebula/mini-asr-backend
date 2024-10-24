from fastapi import FastAPI
from app.api import transcribe, health_check

# 创建 FastAPI 应用实例
app = FastAPI(
    title="Whisper Speech to Text API",
    description="使用 Whisper 模型实现语音转文本的 API 服务。",
    version="1.0.0",
    docs_url="/",
)

# 包含健康检查和音频转录的路由
app.include_router(health_check.router, prefix="/health", tags=["Health Check"])
app.include_router(transcribe.router, prefix="/transcribe", tags=["Transcribe"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


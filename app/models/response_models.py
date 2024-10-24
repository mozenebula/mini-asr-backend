from pydantic import BaseModel


class TranscribeResponse(BaseModel):
    """
    音频转录响应模型
    """
    transcription: str  # 转录后的文本


class HealthCheckResponse(BaseModel):
    """
    健康检查响应模型
    """
    status: str  # 返回 API 的健康状态

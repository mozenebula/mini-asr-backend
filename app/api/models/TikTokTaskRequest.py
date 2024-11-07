from fastapi import Form
from pydantic import HttpUrl

from app.api.models.WhisperTaskRequest import WhisperTaskRequest


class TikTokVideoTask(WhisperTaskRequest):
    url: HttpUrl = Form(
        description="TikTok 视频的 URL 地址 / URL address of the TikTok video",
        example="https://www.tiktok.com/@example/video/1234567890"
    )

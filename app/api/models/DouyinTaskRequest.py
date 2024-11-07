from fastapi import Form
from pydantic import HttpUrl

from app.api.models.WhisperTaskRequest import WhisperTaskRequest


class DouyinVideoTask(WhisperTaskRequest):
    url: HttpUrl = Form(
        description="抖音视频的 URL 地址 / URL address of the Douyin video",
        example="https://v.douyin.com/iANRkr9m/"
    )
    platform: str = Form(
        default="douyin",
        description="指定平台为抖音 / Specify the platform as Douyin"
    )

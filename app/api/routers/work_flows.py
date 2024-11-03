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
import traceback
from typing import Optional, Union, List

from fastapi import APIRouter, Request, HTTPException, Form, BackgroundTasks
from starlette import status

from app.database.models import TaskPriority
from app.utils.logging_utils import configure_logging

from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel

router = APIRouter()

# 配置日志记录器 | Configure the logger
logger = configure_logging(name=__name__)


# 输入一个视频链接，然后创建一个 Whisper 任务 | Input a video link, then create a Whisper task
@router.post("/create_work_flow",
             response_model=ResponseModel,
             summary="创建一个工作流 / Create a work flow",
             response_description="创建工作流的结果信息 / The result information of creating a work flow"
             )
async def create_work_flow(
        request: Request,
        background_tasks: BackgroundTasks,
        media_url: str = Form(description="视频的 URL，用于后台爬取并创建 Whisper 任务 / URL of the media to be crawled and processed"),
        task_type: str = Form("transcribe",
                              description="任务类型，默认为 'transcription'，具体取值请参考文档 / Task type, default is 'transcription', refer to the documentation for specific values"),
        callback_url: Optional[str] = Form("",
                                           description="回调URL，任务完成时通知客户端 / Callback URL to notify the client when the task is completed"),
        priority: TaskPriority = Form(TaskPriority.NORMAL, description="任务优先级 / Task priority"),
        language: str = Form("",
                             description="指定输出语言，例如 'en' 或 'zh'，留空则自动检测 / Specify the output language, e.g., 'en' or 'zh', leave empty for auto-detection"),
        temperature: str = Form("0.8,1.0",
                                description="采样温度，控制输出文本的多样性，可以是单个值或使用逗号分隔的多个值 / Sampling temperature, control the diversity of the output text, can be a single value or multiple values separated by commas"),
        compression_ratio_threshold: float = Form(1.8, description="压缩比阈值 / Compression ratio threshold"),
        no_speech_threshold: float = Form(0.5, description="无声部分的概率阈值 / No-speech probability threshold"),
        condition_on_previous_text: bool = Form(True,
                                                description="在连续语音中更准确地理解上下文 / Condition on previous text"),
        initial_prompt: str = Form("", description="初始提示文本 / Initial prompt text"),
        word_timestamps: bool = Form(False,
                                     description="是否提取每个词的时间戳信息 / Whether to extract word-level timestamp information"),
        prepend_punctuations: str = Form("\"'“¿([{-",
                                         description="前置标点符号集合 / Prepend punctuation characters"),
        append_punctuations: str = Form("\"'.。,，!！?？:：”)]}、",
                                        description="后置标点符号集合 / Append punctuation characters"),
        clip_timestamps: Union[str, List[float]] = Form("0",
                                                        description="裁剪时间戳 / Clip timestamps to avoid out-of-range issues"),
        hallucination_silence_threshold: Optional[float] = Form(None,
                                                                description="幻听静音阈值 / Hallucination silence threshold")
):
    # TODO: 完善工作流创建逻辑 | Improve the workflow creation logic
    try:
        # Step 1: 后台爬取并保存媒体文件 | Crawl and save media files in the background
        response = await request.app.state.crawler_service.download_media(media_url)
        if isinstance(response, dict):
            file_bytes = response.get("file")
            file_name = response.get("file_name")
        else:
            raise RuntimeError("Failed to download media file")

        # Step 2: 设置解码参数 | Set decode options
        decode_options = {
            "language": language if language else None,
            "temperature": [float(temp) for temp in temperature.split(",")] if "," in temperature else float(
                temperature),
            "compression_ratio_threshold": compression_ratio_threshold,
            "no_speech_threshold": no_speech_threshold,
            "condition_on_previous_text": condition_on_previous_text,
            "initial_prompt": initial_prompt,
            "word_timestamps": word_timestamps,
            "prepend_punctuations": prepend_punctuations,
            "append_punctuations": append_punctuations,
            "clip_timestamps": clip_timestamps,
            "hallucination_silence_threshold": hallucination_silence_threshold
        }

        # Step 3: 创建 Whisper 任务
        task_info = await request.app.state.whisper_service.create_whisper_task(
            file=file_bytes,
            file_name=file_name,
            callback_url=callback_url,
            decode_options=decode_options,
            task_type=task_type,
            priority=priority,
            request=request
        )

        # Step 4: 返回任务创建信息
        return ResponseModel(
            code=200,
            router=str(request.url),
            params={"media_url": media_url, "callback_url": callback_url, **decode_options},
            data=task_info.to_dict()
        )

    except HTTPException as http_error:
        raise http_error

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponseModel(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"An unexpected error occurred while creating the video workflow: {str(e)}",
                router=str(request.url),
                params={"media_url": media_url, "callback_url": callback_url, "priority": priority,
                        "language": language},
            ).dict()
        )

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

from typing import Union, List, Optional

from fastapi import Request, APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks, Query, status
from sqlalchemy.exc import SQLAlchemyError

from app.services.whisper_service_instance import whisper_service
from app.utils.logging_utils import configure_logging
from app.database.database import DatabaseManager
from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel
from app.database.models import Task, TaskStatus, TaskPriority

router = APIRouter()

# 配置日志记录器
logger = configure_logging(name=__name__)

# 初始化数据库管理器
db_manager = DatabaseManager()


@router.post(
    "/task/create",
    response_model=ResponseModel,
    summary="上传媒体文件并且创建一个Whisper转录任务在后台处理 | Upload a media file and create a Whisper transcription task to be processed in the background"
)
async def create_transcription_task(
        request: Request,
        file: UploadFile = File(...,
                                description="媒体文件（支持的格式：音频和视频，如 MP3, WAV, MP4, MKV 等） / Media file (supported formats: audio and video, e.g., MP3, WAV, MP4, MKV)"),
        priority: TaskPriority = Form(TaskPriority.NORMAL, description="任务优先级 / Task priority"),
        temperature: Union[float, List[float]] = Form(0.2,
                                                      description="采样温度 / Sampling temperature (can be a single value or a list of values)"),
        verbose: bool = Form(False, description="是否显示详细信息 / Whether to display detailed information"),
        compression_ratio_threshold: float = Form(2.4, description="压缩比阈值 / Compression ratio threshold"),
        logprob_threshold: float = Form(-1.0, description="对数概率阈值 / Log probability threshold"),
        no_speech_threshold: float = Form(0.6, description="无声部分的概率阈值 / No-speech probability threshold"),
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
    try:
        decode_options = {
            "temperature": temperature,
            "verbose": verbose,
            "compression_ratio_threshold": compression_ratio_threshold,
            "logprob_threshold": logprob_threshold,
            "no_speech_threshold": no_speech_threshold,
            "condition_on_previous_text": condition_on_previous_text,
            "initial_prompt": initial_prompt,
            "word_timestamps": word_timestamps,
            "prepend_punctuations": prepend_punctuations,
            "append_punctuations": append_punctuations,
            "clip_timestamps": clip_timestamps,
            "hallucination_silence_threshold": hallucination_silence_threshold
        }
        task_info = await whisper_service.create_transcription_task(
            file=file,
            decode_options=decode_options,
            priority=priority
        )
        return ResponseModel(code=200,
                             router=str(request.url),
                             params=dict(request.query_params),
                             data=task_info.to_dict())
    except Exception as e:
        logger.error(f"Unknown error occurred during transcription: {str(e)}")
        detail = ErrorResponseModel(code=500,
                                    router=str(request.url),
                                    params=dict(request.query_params),
                                    message=f"Failed to create transcription task. An unknown error occurred: {str(e)}",
                                    ).dict()
        raise HTTPException(
            status_code=500,
            detail=detail
        )


@router.get("/tasks/check",
            summary="获取任务状态 / Get task status",
            response_model=ResponseModel)
async def get_task_status(
        request: Request,
        task_id: int = Query(description="任务ID / Task ID")
):
    try:
        async with db_manager.get_session() as session:
            task_info = await session.get(Task, task_id)
            if not task_info:
                raise HTTPException(status_code=404, detail="Task not found in the database.")
            return ResponseModel(code=200,
                                 router=str(request.url),
                                 params=dict(request.query_params),
                                 data=task_info.to_dict())
    except Exception as e:
        logger.error(f"Unknown error occurred during task status check: {str(e)}")
        detail = ErrorResponseModel(code=500,
                                    router=str(request.url),
                                    params=dict(request.query_params),
                                    message=f"Failed to retrieve task status. An unknown error occurred: {str(e)}",
                                    ).dict()
        raise HTTPException(
            status_code=500,
            detail=detail
        )


@router.get("/tasks/result",
            summary="获取任务结果 / Get task result",
            response_model=ResponseModel)
async def get_task_result(
    request: Request,
    task_id: int = Query(description="任务ID / Task ID")
):
    try:
        async with db_manager.get_session() as session:
            task = await session.get(Task, task_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=ErrorResponseModel(
                        code=status.HTTP_404_NOT_FOUND,
                        message="Task not found.",
                        router=str(request.url),
                        params=dict(request.query_params),
                    ).dict()
                )
            if task.status != TaskStatus.COMPLETED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorResponseModel(
                        code=status.HTTP_400_BAD_REQUEST,
                        message="Task is not completed yet.",
                        router=str(request.url),
                        params=dict(request.query_params),
                    ).dict()
                )
            return ResponseModel(
                code=status.HTTP_200_OK,
                router=str(request.url),
                params=dict(request.query_params),
                data=task.to_dict()
            )

    except SQLAlchemyError as db_error:
        logger.error(f"Database error: {str(db_error)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ErrorResponseModel(
                code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="Database error occurred. Please try again later.",
                router=str(request.url),
                params=dict(request.query_params),
            ).dict()
        )

    except HTTPException as http_exc:
        # Directly re-raise HTTPExceptions
        raise http_exc

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponseModel(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="An unexpected error occurred while retrieving the task result.",
                router=str(request.url),
                params=dict(request.query_params),
            ).dict()
        )


@router.post("/extract-audio",
             summary="从视频文件中提取音频 / Extract audio from a video file")
async def extract_audio(
        file: UploadFile = File(...,
                                description="视频文件，支持的格式如 MP4, MKV 等 / Video file, supported formats like MP4, MKV etc."),
        sample_rate: int = Form(22050, description="音频的采样率（单位：Hz），例如 22050 或 44100。"),
        bit_depth: int = Form(2, description="音频的位深度（1 或 2 字节），决定音频的质量和文件大小。"),
        output_format: str = Form("wav", description="输出音频的格式，可选 'wav' 或 'mp3'。"),
        background_tasks: BackgroundTasks = None
):
    """
    提取视频文件中的音频部分。

    参数 | Parameters:
        file (UploadFile): 上传的视频文件。
        sample_rate (int): 采样率。
        bit_depth (int): 位深度。
        output_format (str): 输出格式，'wav' 或 'mp3'。
        background_tasks (BackgroundTasks): FastAPI 的后台任务。

    返回 | Returns:
        FileResponse: 包含音频文件的响应。
    """
    try:
        response = await whisper_service.extract_audio_from_video(
            file=file,
            sample_rate=sample_rate,
            bit_depth=bit_depth,
            output_format=output_format,
            background_tasks=background_tasks
        )
        logger.info(f"Audio extracted successfully from video file: {file.filename}")
        return response
    except HTTPException as e:
        logger.error(f"HTTPException during audio extraction: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"Unknown error occurred during audio extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to extract audio: {str(e)}")

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
from typing import Union, List, Optional

from fastapi import Request, APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks, Query, status
from sqlalchemy.exc import SQLAlchemyError

from app.utils.logging_utils import configure_logging
from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel
from app.database.models import Task, TaskStatus, TaskPriority

router = APIRouter()

# 配置日志记录器
logger = configure_logging(name=__name__)


# 在后台创建一个转录任务 | Create a transcription task in the background
@router.post(
    "/task/create",
    response_model=ResponseModel,
    summary="上传媒体文件并且创建一个Whisper转录任务在后台处理 | Upload a media file and create a Whisper transcription task to be processed in the background"
)
async def create_transcription_task(
        request: Request,
        file: UploadFile = File(...,
                                description="媒体文件（支持的格式：音频和视频，如 MP3, WAV, MP4, MKV 等） / Media file (supported formats: audio and video, e.g., MP3, WAV, MP4, MKV)"),
        task_type: str = Form("transcribe",
                              description="任务类型，默认为 'transcription'，具体取值请参考文档 / Task type, default is 'transcription', refer to the documentation for specific values"),
        priority: TaskPriority = Form(TaskPriority.NORMAL, description="任务优先级 / Task priority"),
        language: str = Form("",
                             description="指定输出语言，例如 'en' 或 'zh'，留空则自动检测 / Specify the output language, e.g., 'en' or 'zh', leave empty for auto-detection"),
        temperature: Union[float, List[float]] = Form(0.2,
                                                      description="采样温度 / Sampling temperature (can be a single value or a list of values)"),
        compression_ratio_threshold: float = Form(2.4, description="压缩比阈值 / Compression ratio threshold"),
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
    """
    # [中文]

    ### 用途说明:

    - 上传媒体文件并且创建一个Whisper任务在后台处理。
    - 任务的处理优先级可以通过`priority`参数指定。
    - 任务的类型可以通过`task_type`参数指定。
    - 任务的处理不是实时的，这样的好处是可以避免线程阻塞，提高性能。
    - 可以通过`/tasks/check`和`/tasks/result`接口查询任务状态和结果。
    - 后续会提供一个回调接口，用于在任务完成时通知客户端。

    ### 参数说明:

    - `file` (UploadFile): 上传的媒体文件，支持Ffmpeg支持的音频和视频格式。
    - `task_type` (str): 任务类型，默认为 'transcription'，具体取值如下。
        - 当后端使用`openai_whisper`引擎时，支持如下取值:
            - `transcribe`: 转录任务。
            - `translate`: 根据`language`参数指定的语言进行翻译任务。
        - 当后端使用`faster_whisper`引擎时，支持如下取值:
            - `transcribe`: 转录任务。
            - `translate`: 根据`language`参数指定的语言进行翻译任务。
    - `priority` (TaskPriority): 任务优先级，默认为 `TaskPriority.NORMAL`。
    - `language` (str): 指定输出语言，例如 'en' 或 'zh'，留空则自动检测。
    - `temperature` (Union[float, List[float]]): 采样温度，可以是单个值或值列表，默认为 0.2。
    - `compression_ratio_threshold` (float): 压缩比阈值，默认为 2.4。
    - `no_speech_threshold` (float): 无声部分的概率阈值，默认为 0.6。
    - `condition_on_previous_text` (bool): 在连续语音中更准确地理解上下文，默认为 True。
    - `initial_prompt` (str): 初始提示文本，默认为空。
    - `word_timestamps` (bool): 是否提取每个词的时间戳信息，默认为 False。
    - `prepend_punctuations` (str): 前置标点符号集合，默认为 "\"'“¿([{-"。
    - `append_punctuations` (str): 后置标点符号集合，默认为 "\"'.。,，!！?？:：”)]}、"。
    - `clip_timestamps` (Union[str, List[float]]): 裁剪时间戳，避免超出范围问题，默认为 "0"。
    - `hallucination_silence_threshold` (Optional[float]): 幻听静音阈值，默认为 None。

    ### 返回:

    - 返回一个包含任务信息的响应，包括任务ID、状态、优先级等信息。

    ### 错误代码说明:

    - `500`: 未知错误。

    # [English]

    ### Purpose:

    - Upload a media file and create a Whisper task to be processed in the background.
    - The processing priority of the task can be specified using the `priority` parameter.
    - The type of task can be specified using the `task_type` parameter.
    - The processing of the task is not real-time, which avoids thread blocking and improves performance.
    - The status and results of the task can be queried using the `/tasks/check` and `/tasks/result` endpoints.
    - A callback endpoint will be provided in the future to notify the client when the task is completed.

    ### Parameters:

    - `file` (UploadFile): The uploaded media file, supporting audio and video formats supported by Ffmpeg.
    - `task_type` (str): The type of
    task, default is 'transcription', specific values are as follows.
        - When the backend uses the 'openai_whisper' engine, the following values are supported:
            - `transcribe`: Transcription task.
            - `translate`: Translation task based on the language specified by the `language` parameter.
        - When the backend uses the 'faster_whisper' engine, the following values are supported:
            - `transcribe`: Transcription task.
            - `translate`: Translation task based on the language specified by the `language` parameter.
    - `priority` (TaskPriority): Task priority, default is `TaskPriority.NORMAL`.
    - `language` (str): Specify the output language, e.g., 'en' or 'zh', leave empty for auto-detection.
    - `temperature` (Union[float, List[float]]): Sampling temperature, can be a single value or a list of values, default is 0.2.
    - `compression_ratio_threshold` (float): Compression ratio threshold, default is 2.4.
    - `no_speech_threshold` (float): No-speech probability threshold, default is 0.6.
    - `condition_on_previous_text` (bool): Condition on previous text for more accurate understanding of context in continuous speech, default is True.
    - `initial_prompt` (str): Initial prompt text, default is empty.
    - `word_timestamps` (bool): Whether to extract word-level timestamp information, default is False.
    - `prepend_punctuations` (str): Prepend punctuation characters, default is "\"'“¿([{-".
    - `append_punctuations` (str): Append punctuation characters, default is "\"'.。,，!！?？:：”)]}、".
    - `clip_timestamps` (Union[str, List[float]]): Clip timestamps to avoid out-of-range issues, default is "0".
    - `hallucination_silence_threshold` (Optional[float]): Hallucination silence threshold, default is None.

    ### Returns:

    - Returns a response containing task information, including task ID, status, priority, etc.

    ### Error Code Description:

    - `500`: Unknown error.
    """
    try:
        decode_options = {
            "language": language if language else None,
            "temperature": temperature,
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
        task_info = await request.app.state.whisper_service.create_transcription_task(
            file=file,
            decode_options=decode_options,
            task_type=task_type,
            priority=priority,
            request=request
        )
        return ResponseModel(code=200,
                             router=str(request.url),
                             params=decode_options | {"task_type": task_type, "priority": priority},
                             data=task_info.to_dict())
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponseModel(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"An unexpected error occurred while creating the transcription task: {str(e)}",
                router=str(request.url),
                params=dict(request.query_params),
            ).dict()
        )


# 获取任务状态 | Get task status
@router.get("/tasks/check",
            summary="获取任务状态 / Get task status",
            response_model=ResponseModel)
async def get_task_status(
        request: Request,
        task_id: int = Query(description="任务ID / Task ID")
):
    """
    # [中文]

    ### 用途说明:
    - 获取指定任务的状态信息。

    ### 参数说明:
    - `task_id` (int): 任务ID。

    ### 返回:
    - 返回一个包含任务状态信息的响应，包括任务ID、状态、优先级等信息。

    ### 错误代码说明:

    - `404`: 任务未找到，可能是任务ID不存在。
    - `500`: 未知错误。

    # [English]

    ### Purpose:
    - Get the status information of the specified task.

    ### Parameters:
    - `task_id` (int): Task ID.

    ### Returns:
    - Returns a response containing task status information, including task ID, status, priority, etc.

    ### Error Code Description:

    - `404`: Task not found, possibly because the task ID does not exist.
    - `500`: Unknown error.
    """
    try:
        async with request.app.state.db_manager.get_session() as session:
            task_info = await session.get(Task, task_id)
            if not task_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=ErrorResponseModel(
                        code=status.HTTP_404_NOT_FOUND,
                        message="Task not found.",
                        router=str(request.url),
                        params=dict(request.query_params),
                    ).dict()
                )
            return ResponseModel(code=200,
                                 router=str(request.url),
                                 params=dict(request.query_params),
                                 data=task_info.to_dict())

    except HTTPException as http_error:
        raise http_error

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponseModel(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"An unexpected error occurred while retrieving the task status: {str(e)}",
                router=str(request.url),
                params=dict(request.query_params),
            ).dict()
        )


@router.get("/tasks/result",
            summary="获取任务结果 / Get task result",
            response_model=ResponseModel)
async def get_task_result(
        request: Request,
        task_id: int = Query(description="任务ID / Task ID")
):
    """
    # [中文]

    ### 用途说明:
    - 获取指定任务的结果信息。

    ### 参数说明:
    - `task_id` (int): 任务ID。

    ### 返回:
    - 返回一个包含任务结果信息的响应，包括任务ID、状态、优先级等信息。

    ### 错误代码说明:

    - `404`: 任务未找到，可能是任务ID不存在。
    - `202`: 任务尚未完成。
    - `503`: 数据库错误。
    - `500`: 未知错误。

    # [English]

    ### Purpose:
    - Get the result information of the specified task.

    ### Parameters:
    - `task_id` (int): Task ID.

    ### Returns:
    - Returns a response containing task result information, including task ID, status, priority, etc.

    ### Error Code Description:

    - `404`: Task not found, possibly because the task ID does not exist.
    - `202`: The task is not yet completed.
    - `503`: Database error.
    - `500`: Unknown error.
    """
    try:
        async with request.app.state.db_manager.get_session() as session:
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
                    status_code=status.HTTP_202_ACCEPTED,
                    detail=ErrorResponseModel(
                        code=status.HTTP_202_ACCEPTED,
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

    except HTTPException as http_error:
        raise http_error

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponseModel(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"An unexpected error occurred while retrieving the task result: {str(e)}",
                router=str(request.url),
                params=dict(request.query_params),
            ).dict()
        )


@router.post("/extract-audio",
             summary="从视频文件中提取音频 / Extract audio from a video file")
async def extract_audio(
        request: Request,
        file: UploadFile = File(...,
                                description="视频文件，支持的格式如 MP4, MKV 等 / Video file, supported formats like MP4, MKV etc."),
        sample_rate: int = Form(22050, description="音频的采样率（单位：Hz），例如 22050 或 44100。"),
        bit_depth: int = Form(2, description="音频的位深度（1 或 2 字节），决定音频的质量和文件大小。"),
        output_format: str = Form("wav", description="输出音频的格式，可选 'wav' 或 'mp3'。"),
        background_tasks: BackgroundTasks = None
):
    """
    # [中文]

    ### 用途说明:

    - 从视频文件中提取音频。

    ### 参数说明:

    - `file` (UploadFile): 上传的视频文件。
    - `sample_rate` (int): 采样率。
    - `bit_depth` (int): 位深度。
    - `output_format` (str): 输出格式，'wav' 或 'mp3'。

    ### 返回:

    - 包含音频文件的响应。

    ### 错误代码说明:

    - `500`: 未知错误。

    # [English]

    ### Purpose:

    - Extract audio from a video file.

    ### Parameters:

    - `file` (UploadFile): The uploaded video file.
    - `sample_rate` (int): The sample rate.
    - `bit_depth` (int): The bit depth.
    - `output_format` (str): The output format, 'wav' or 'mp3'.

    ### Returns:

    - A response containing the audio file.

    ### Error Code Description:

    - `500`: Unknown error.
    """
    try:
        response = await request.app.state.whisper_service.extract_audio_from_video(
            file=file,
            sample_rate=sample_rate,
            bit_depth=bit_depth,
            output_format=output_format,
            background_tasks=background_tasks
        )
        logger.info(f"Audio extracted successfully from video file: {file.filename}")
        return response
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponseModel(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"An unexpected error occurred while extracting audio from the video file: {str(e)}",
                router=str(request.url),
                params=dict(request.query_params),
            ).dict()
        )

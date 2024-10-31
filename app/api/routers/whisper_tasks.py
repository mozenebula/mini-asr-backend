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
from app.database.models import Task, TaskStatus, TaskPriority, QueryTasksOptionalFilter

router = APIRouter()

# 配置日志记录器
logger = configure_logging(name=__name__)


# 创建任务 | Create task
@router.post(
    "/task/create",
    response_model=ResponseModel,
    summary="上传媒体文件并且创建一个Whisper转录任务在后台处理 | Upload a media file and create a Whisper transcription task to be processed in the background"
)
async def task_create(
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


# 查询任务 | Query task
@router.post("/tasks/query",
             response_model=ResponseModel,
             summary="查询任务 | Query task"
             )
async def task_query(
        request: Request,
        params: QueryTasksOptionalFilter
):
    """
    # [中文]

    ### 用途说明:
    - 根据多种筛选条件查询任务列表，包括任务状态、优先级、创建时间、语言、引擎名称等信息。
    - 该接口适用于分页查询，并且通过 `limit` 和 `offset` 参数控制每页显示的记录数，支持客户端逐页加载数据。

    ### 参数说明:
    - `status` (TaskStatus): 筛选任务状态：
        - 例如 'queued'（排队中）或 'processing'（处理中）或 'completed'（已完成） 或 'failed'（失败）。
    - `priority` (TaskPriority): 筛选任务优先级：
        - 例如 'low'、'normal'、'high'。
    - `created_after` (str): 创建时间的起始时间，格式为 'YYYY-MM-DDTHH:MM:SS'，为空时忽略该条件。
    - `created_before` (str): 创建时间的结束时间，格式为 'YYYY-MM-DDTHH:MM:SS'，为空时忽略该条件。
    - `language` (str): 任务的语言代码，例如 `zh`或'en'。设置为空字符串 `""` 可以查询所有语言的任务。
    - `engine_name` (str): 引擎名称，例如 'faster_whisper'或'openai_whisper'。
    - `has_result` (bool): 指定是否要求任务有结果数据。
    - `has_error` (bool): 指定是否要求任务有错误信息。
    - `limit` (int): 每页的记录数量，默认值为20，用户可根据需求自定义每页数量。
    - `offset` (int): 数据分页的起始位置，默认值为0，后续使用响应中的 `next_offset` 值进行下一页查询。

    ### 返回:
    - `tasks` (list): 包含满足条件的任务列表，每个任务记录包括任务ID、状态、优先级、创建时间等详细信息。
    - `total_count` (int): 符合条件的任务总数。
    - `has_more` (bool): 是否还有更多数据。如果为 `True`，则表示存在下一页数据。
    - `next_offset` (int): 下次分页请求的偏移量。用户可以通过此值构建下一页查询请求。

    ### 使用示例:
    - 请求示例：
        ```json
        {
            "status": "completed",
            "priority": "high",
            "created_after": "2024-01-01T00:00:00",
            "created_before": "2024-12-31T23:59:59",
            "language": "",
            "engine_name": "faster_whisper",
            "has_result": true,
            "has_error": false,
            "limit": 10,
            "offset": 0
        }
        ```
    - 响应示例：
        ```json
        {
            "code": 200,
            "router": "http://localhost/api/tasks/query",
            "params": { ... },
            "data": {
                "tasks": [
                    {
                        "id": 123,
                        "status": "completed",
                        "priority": "high",
                        "created_at": "2024-05-15T12:34:56",
                        "language": "en",
                        "engine_name": "faster_whisper",
                        "result": {...},
                        "error_message": null
                    },
                    ...
                ],
                "total_count": 55,
                "has_more": true,
                "next_offset": 10
            }
        }
        ```

    ### 错误代码说明:
    - `500`: 未知错误，通常为内部错误。

    # [English]

    ### Purpose:
    - Query the task list based on multiple filtering conditions, including task status, priority, creation time, language, engine name, etc.
    - This endpoint is suitable for paginated queries, and the number of records displayed per page is controlled by the `limit` and `offset` parameters, supporting clients to load data page by page.

    ### Parameters:
    - `status` (TaskStatus): Filter task status:
        - e.g., 'queued' (in the queue), 'processing' (processing), 'completed' (completed), or 'failed' (failed).
    - `priority` (TaskPriority): Filter task priority:
        - e.g., 'low', 'normal', 'high'.
    - `created_after` (str): Start time of creation time, format is 'YYYY-MM-DDTHH:MM:SS', ignore this condition when empty.
    - `created_before` (str): End time of creation time, format is 'YYYY-MM-DDTHH:MM:SS', ignore this condition when empty.
    - `language` (str): Language code of the task, e.g., `zh` or `en`. Set to an empty string `""` to query tasks in all languages.
    - `engine_name` (str): Engine name, e.g., 'faster_whisper' or 'openai_whisper'.
    - `has_result` (bool): Specify whether the task requires result data.
    - `has_error` (bool): Specify whether the task requires error information.
    - `limit` (int): Number of records per page, default is 20, users can customize the number of records per page according to their needs.
    - `offset` (int): Starting position of data pagination, default is 0, use the `next_offset` value in the response for the next page query.

    ### Returns:
    - `tasks` (list): List of tasks that meet the conditions, each task record includes detailed information such as task ID, status, priority, creation time, etc.
    - `total_count` (int): Total number of tasks that meet the conditions.
    - `has_more` (bool): Whether there is more data. If `True`, it means there is more data on the next page.
    - `next_offset` (int): Offset value for the next page request. Users can use this value to construct the next page query request.

    ### Example:
    - Request example:
        ```json
        {
            "status": "completed",
            "priority": "high",
            "created_after": "2024-01-01T00:00:00",
            "created_before": "2024-12-31T23:59:59",
            "language": "",
            "engine_name": "faster_whisper",
            "has_result": true,
            "has_error": false,
            "limit": 10,
            "offset": 0
        }
        ```
    - Response example:
        ```json
        {
            "code": 200,
            "router": "http://localhost/api/tasks/query",
            "params": { ... },
            "data": {
                "tasks": [
                    {
                        "id": 123,
                        "status": "completed",
                        "priority": "high",
                        "created_at": "2024-05-15T12:34:56",
                        "language": "en",
                        "engine_name": "faster_whisper",
                        "result": {...},
                        "error_message": null
                    },
                    ...
                ],
                "total_count": 55,
                "has_more": true,
                "next_offset": 10
            }
        }
        ```

    ### Error Code Description:
    - `500`: Unknown error, usually an internal error.
    """

    async with request.app.state.db_manager.get_session() as session:
        result = await request.app.state.db_manager.query_tasks(session, params)
        if result is None:
            raise HTTPException(status_code=500, detail="An error occurred while querying tasks.")

    return ResponseModel(
        code=200,
        router=str(request.url),
        params=params.dict(),
        data=result
    )


@router.get("/tasks/result",
            summary="获取任务结果 / Get task result",
            response_model=ResponseModel)
async def task_result(
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

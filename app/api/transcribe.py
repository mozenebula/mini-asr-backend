import json

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks

from app.services.whisper_service_instance import whisper_service
from app.utils.logging_utils import configure_logging
from app.services.tasks import Task, TaskStatus, SessionLocal

router = APIRouter()

# 配置日志记录器
logger = configure_logging(name=__name__)


@router.post(
    "/",
    summary="上传媒体文件并将其转换为文本 / Upload a media file and convert it to text"
)
async def transcribe(
        file: UploadFile = File(...,
                                description="媒体文件（支持的格式：音频和视频，如 MP3, WAV, MP4, MKV 等） / Media file (supported formats: audio and video, e.g., MP3, WAV, MP4, MKV)"),
        temperature: float = Form(0.2, description="采样温度 / Sampling temperature"),
        verbose: bool = Form(True, description="是否显示详细信息 / Whether to display detailed information"),
        compression_ratio_threshold: float = Form(2.4, description="压缩比阈值 / Compression ratio threshold"),
        logprob_threshold: float = Form(-1.0, description="对数概率阈值 / Log probability threshold"),
        no_speech_threshold: float = Form(0.6, description="无声部分的概率阈值 / No-speech probability threshold"),
        condition_on_previous_text: bool = Form(True,
                                                description="在连续语音中更准确地理解上下文 / Condition on previous text"),
        initial_prompt: str = Form("", description="初始提示文本 / Initial prompt text"),
        word_timestamps: bool = Form(False,
                                     description="是否提取每个词的时间戳信息 / Whether to extract word-level timestamp information")
):
    """
    上传媒体文件并将其转换为文本 | Upload a media file and convert it to text.

    返回任务ID，客户端可以根据任务ID查询任务状态和结果。
    Return task ID, client can query task status and result using the task ID.
    """
    try:
        decode_options = {
            "temperature": temperature,
            "verbose": verbose,
            "compression_ratio_threshold": compression_ratio_threshold,
            "logprob_threshold": logprob_threshold,
            "no_speech_threshold": no_speech_threshold,
            "condition_on_previous_text": condition_on_previous_text,
            "initial_prompt": initial_prompt,
            "word_timestamps": word_timestamps
        }
        task_id = await whisper_service.create_transcription_task(
            file=file,
            decode_options=decode_options
        )
        return {"task_id": task_id, "message": "Task submitted successfully."}
    except HTTPException as e:
        logger.error(f"HTTPException during transcription: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"Unknown error occurred during transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"媒体转录过程中发生了未知错误：{str(e)}。请检查媒体文件是否正确。")


@router.get("/tasks/{task_id}", summary="获取任务状态 / Get task status")
async def get_task_status(task_id: int):
    with SessionLocal() as session:
        task = session.query(Task).get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found.")
        return {
            "task_id": task.id,
            "status": task.status.value,
            "error": task.error
        }


@router.get("/tasks/{task_id}/result", summary="获取任务结果 / Get task result")
async def get_task_result(task_id: int):
    with SessionLocal() as session:
        task = session.query(Task).get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found.")
        if task.status != TaskStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Task is not completed yet.")
        return {
            "task_id": task.id,
            "result": json.loads(task.result)  # Assuming result is stored as JSON string
        }


@router.post("/extract-audio/",
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
        raise HTTPException(status_code=500, detail=f"音频提取过程中发生了未知错误：{str(e)}。请检查视频文件是否正确。")

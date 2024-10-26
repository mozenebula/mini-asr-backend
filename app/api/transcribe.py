import logging

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks

from app.services.whisper_service import WhisperService
from app.utils.logging_utils import configure_logging

router = APIRouter()

# 配置日志记录器
logger = configure_logging(name=__name__)

# 实例化 WhisperService
whisper_service = WhisperService()


@router.post(
    "/",
    response_model=None,
    summary="上传媒体文件并将其转换为文本 / Upload a media file and convert it to text"
)
async def transcribe(
        file: UploadFile = File(...,
                                description="媒体文件（支持的格式：音频和视频，如 MP3, WAV, MP4, MKV 等） / Media file (supported formats: audio and video, e.g., MP3, WAV, MP4, MKV)"),
        speed_multiplier: float = Form(1.0,
                                       description="倍速因子，例如2.0表示2倍速（过高可能会影响精确性） / Speed multiplier, e.g., 2.0 for double speed (higher values may reduce accuracy)"),
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
    # [中文]

    ### 接口说明：
    - 这个接口允许用户上传一个媒体文件（如音频、视频等），并使用Whisper模型将其转录为文本。
    - Whisper模型支持多种格式，包括音频（如MP3, WAV）和视频（如MP4, MKV），并利用ffmpeg进行格式处理。
    - 默认参数经过优化，以确保转录的准确性和性能。

    ### 参数说明：
    - `file` 必填参数，用于上传媒体文件，支持的格式包括音频和视频（如MP3, WAV, MP4, MKV等）。
    - `speed_multiplier` 可选参数，默认为`1.0`，参数允许调整音频的播放速度（如2倍速），过高的速度可能导致精度下降。
    - `temperature` 可选参数，默认为`0.2`，用于控制采样温度。
    - `verbose` 可选参数，默认为`True`，用于控制是否显示详细信息。
    - `compression_ratio_threshold` 可选参数，默认为`2.4`，用于控制压缩比阈值。
    - `logprob_threshold` 可选参数，默认为`-1.0`，用于控制对数概率阈值。
    - `no_speech_threshold` 可选参数，默认为`0.6`，用于控制无声部分的概率阈值。
    - `condition_on_previous_text` 可选参数，默认为`True`，用于控制是否基于前一个输出作为下一窗口的提示。
    - `initial_prompt` 可选参数，默认为空字符串，用于指定初始提示文本。
    - `word_timestamps` 可选参数，默认为`False`，用于控制是否提取每个词的时间戳信息。

    # [English]

    ### API Description:
    - This API allows users to upload a media file (e.g., audio, video) and transcribe it to text using the Whisper model.
    - The Whisper model supports various formats, including audio (e.g., MP3, WAV) and video (e.g., MP4, MKV), and utilizes ffmpeg for format processing.
    - Default parameters are optimized to ensure transcription accuracy and performance.

    ### Parameters:
    - `file` is a required parameter for uploading media files, supporting formats such as audio and video (e.g., MP3, WAV, MP4, MKV, etc.).
    - `speed_multiplier` is an optional parameter, defaulting to `1.0`, allowing adjustment of audio playback speed (e.g., 2x speed), with higher speeds potentially reducing accuracy.
    - `temperature` is an optional parameter, defaulting to `0.2`, used to control sampling temperature.
    - `verbose` is an optional parameter, defaulting to `True`, used to control whether detailed information is displayed.
    - `compression_ratio_threshold` is an optional parameter, defaulting to `2.4`, used to control the compression ratio threshold.
    - `logprob_threshold` is an optional parameter, defaulting to `-1.0`, used to control the log probability threshold.
    - `no_speech_threshold` is an optional parameter, defaulting to `0.6`, used to control the no-speech probability threshold.
    - `condition_on_previous_text` is an optional parameter, defaulting to `True`, used to control whether the previous output is based on the next window prompt.
    - `initial_prompt` is an optional parameter, defaulting to an empty string, used to specify the initial prompt text.
    - `word_timestamps` is an optional parameter, defaulting to `False`, used to control whether word-level timestamp information is extracted.
    """
    try:
        # 调用 WhisperService 的 transcribe_audio 方法
        transcription = await whisper_service.transcribe_audio(
            file=file,
            speed_multiplier=speed_multiplier,
            temperature=temperature,
            verbose=verbose,
            compression_ratio_threshold=compression_ratio_threshold,
            logprob_threshold=logprob_threshold,
            no_speech_threshold=no_speech_threshold,
            condition_on_previous_text=condition_on_previous_text,
            initial_prompt=initial_prompt,
            word_timestamps=word_timestamps
        )
        logger.info(f"Transcription successful for file: {file.filename}")
    except HTTPException as e:
        logger.error(f"HTTPException during transcription: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"Unknown error occurred during transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"媒体转录过程中发生了未知错误：{str(e)}。请检查媒体文件是否正确。")

    return transcription


@router.post("/extract-audio/",
             response_model=None,
             summary="从视频文件中提取音频 / Extract audio from a video file")
async def extract_audio(
        file: UploadFile = File(...),
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

import os
import uuid
from typing import Optional

from fastapi import UploadFile, HTTPException, BackgroundTasks
import whisper
import torch
from pydub import AudioSegment
from fastapi.responses import FileResponse
from moviepy.editor import VideoFileClip

# 文件相关处理 | File-related operations
from app.utils.file_utils import FileUtils
from app.utils.logging_utils import configure_logging


class WhisperService:
    """
    Whisper 服务类，用于处理音频和视频的转录和音频提取。
    Whisper service class for audio transcription and audio extraction from videos.
    """

    def __init__(self, model_name: str = "large-v3", temp_dir: str = "./Temp_Files") -> None:
        """
        初始化 WhisperService 实例。

        参数 | Parameters:
            model_name (str): Whisper 模型名称，默认为 "large-v3"。
            temp_dir (str): 临时文件目录，默认为 "Temp_Files"。

        返回 | Returns:
            None
        """
        # 配置日志记录器
        self.logger = configure_logging(name=__name__)

        # 初始化 FileUtils 实例
        self.file_utils = FileUtils(temp_dir=temp_dir)

        # 初始化 CUDA
        try:
            torch.cuda.init()
            self.logger.info("CUDA initialized successfully.")
        except Exception as e:
            self.logger.warning(f"Failed to initialize CUDA: {str(e)}")

        # 选择设备和加载模型
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self.logger.info(f"Loading Whisper model '{self.model_name}' on device '{self.device}'.")
        try:
            self.model = whisper.load_model(self.model_name, device=self.device)
            self.logger.info(f"Model '{self.model_name}' loaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model '{self.model_name}': {str(e)}")
            raise RuntimeError(f"Failed to load model '{self.model_name}': {e}")

    async def transcribe_audio(
            self,
            file: UploadFile,
            speed_multiplier: float = 1.0,
            **decode_options
    ) -> dict:
        """
        转录音频文件 | Transcribe an audio file.

        参数 | Parameters:
            file (UploadFile): 上传的音频文件 | Uploaded audio file.
            speed_multiplier (float): 速度倍率 | Speed multiplier.
            **decode_options: 解码选项 | Decoding options.

        返回 | Returns:
            dict: 转录结果 | Transcription result.
        """
        self.logger.debug(f"Starting transcription for file: {file.filename}")
        # 保存上传的音频文件
        temp_file_path = await self.file_utils.save_uploaded_file(file)
        self.logger.debug(f"Audio file saved to temporary path: {temp_file_path}")
        temp_files_to_delete = [temp_file_path]  # 记录需要删除的临时文件
        try:
            if speed_multiplier != 1.0:
                self.logger.debug(f"Adjusting audio speed by a factor of {speed_multiplier}")
                # 调整音频速度
                audio = AudioSegment.from_file(temp_file_path)
                audio = audio.speedup(playback_speed=speed_multiplier)

                # 生成新的临时文件路径
                temp_fast_path = os.path.join(
                    self.file_utils.TEMP_DIR,
                    f"{uuid.uuid4().hex}_fast.mp3"
                )
                audio.export(temp_fast_path, format="mp3")
                self.logger.debug(f"Adjusted audio saved to: {temp_fast_path}")
                temp_files_to_delete.append(temp_fast_path)
                temp_file_path = temp_fast_path

            # 调用 Whisper 模型进行转录
            self.logger.info(f"Transcribing audio file: {temp_file_path}")
            result = self.model.transcribe(temp_file_path, **decode_options)
            self.logger.info(f"Transcription completed for file: {file.filename}")
            return result
        except Exception as e:
            self.logger.error(f"Audio processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail="音频处理失败")
        finally:
            # 删除所有临时文件
            for path in temp_files_to_delete:
                if os.path.exists(path):
                    await self.file_utils.delete_file(path)
                    self.logger.debug(f"Deleted temporary file: {path}")

    async def extract_audio_from_video(
            self,
            file: UploadFile,
            sample_rate: int,
            bit_depth: int,
            output_format: str,
            background_tasks: Optional[BackgroundTasks] = None
    ):
        """
        从视频文件中提取音频 | Extract audio from a video file.

        参数 | Parameters:
            file (UploadFile): 上传的视频文件 | Uploaded video file.
            sample_rate (int): 采样率 | Sample rate.
            bit_depth (int): 位深度 | Bit depth.
            output_format (str): 输出音频格式 | Output audio format.
            background_tasks (Optional[BackgroundTasks]): FastAPI 后台任务，用于在响应后删除临时文件.

        返回 | Returns:
            FileResponse: 包含音频文件的响应 | Response containing the audio file.
        """
        self.logger.debug(f"Starting audio extraction from video file: {file.filename}")

        if not file.content_type.startswith("video/"):
            self.logger.warning(f"Invalid content type: {file.content_type}")
            raise HTTPException(status_code=400, detail="仅支持视频文件。")

        # 保存上传的视频文件
        temp_video_path = await self.file_utils.save_uploaded_file(file)
        self.logger.debug(f"Video file saved to temporary path: {temp_video_path}")
        temp_files_to_delete = [temp_video_path]  # 记录需要删除的临时文件
        try:
            # 打开视频文件
            self.logger.debug(f"Opening video file: {temp_video_path}")
            video_clip = VideoFileClip(temp_video_path)

            # 生成临时文件路径
            temp_audio_file_name = f"{uuid.uuid4().hex}.{output_format}"
            temp_audio_path = os.path.join(self.file_utils.TEMP_DIR, temp_audio_file_name)
            wav_temp_file_name = f"{uuid.uuid4().hex}.wav"
            wav_temp_path = os.path.join(self.file_utils.TEMP_DIR, wav_temp_file_name)
            temp_files_to_delete.append(wav_temp_path)

            # 将视频文件中的音频提取为临时 WAV 文件
            self.logger.info(f"Extracting audio to WAV file: {wav_temp_path}")
            video_clip.audio.write_audiofile(wav_temp_path, fps=sample_rate, nbytes=bit_depth)
            self.logger.debug(f"Audio extracted to WAV file: {wav_temp_path}")

            # 关闭视频剪辑
            video_clip.close()

            if output_format == "wav":
                temp_audio_path = wav_temp_path
                self.logger.debug("Output format is WAV; using extracted WAV file directly.")
            elif output_format == "mp3":
                # 使用 pydub 进行格式转换
                self.logger.info(f"Converting WAV to MP3: {temp_audio_path}")
                audio = AudioSegment.from_wav(wav_temp_path)
                audio.export(temp_audio_path, format="mp3")
                self.logger.debug(f"Audio converted to MP3: {temp_audio_path}")
                temp_files_to_delete.append(temp_audio_path)
            else:
                self.logger.warning(f"Unsupported output format: {output_format}")
                raise HTTPException(status_code=400, detail="不支持的音频格式，仅支持 'wav' 和 'mp3'。")

            # 在响应后删除临时文件
            if background_tasks:
                self.logger.debug("Adding temporary files to background tasks for deletion.")
                for path in temp_files_to_delete:
                    if os.path.exists(path):
                        background_tasks.add_task(self.file_utils.delete_file, path)
            else:
                # 如果没有提供 background_tasks，则立即删除文件
                self.logger.debug("No background tasks provided; deleting temporary files immediately.")
                for path in temp_files_to_delete:
                    if os.path.exists(path):
                        await self.file_utils.delete_file(path)
                        self.logger.debug(f"Deleted temporary file: {path}")

            # 返回音频文件的响应
            self.logger.info(f"Returning extracted audio file: {temp_audio_path}")
            return FileResponse(
                temp_audio_path,
                media_type=f"audio/{output_format}",
                filename=f"extracted_audio.{output_format}",
            )
        except Exception as e:
            self.logger.error(f"Audio extraction failed: {str(e)}")
            # 删除所有临时文件
            for path in temp_files_to_delete:
                if os.path.exists(path):
                    await self.file_utils.delete_file(path)
                    self.logger.debug(f"Deleted temporary file after failure: {path}")
            raise HTTPException(status_code=500, detail=f"音频提取失败: {e}")
        finally:
            # 确保视频剪辑被关闭
            if 'video_clip' in locals():
                video_clip.close()
                self.logger.debug("Video clip closed.")

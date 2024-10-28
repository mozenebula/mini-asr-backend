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
import asyncio
import os
import uuid
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import torch
import whisper
from fastapi import Request, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from moviepy.video.io.VideoFileClip import VideoFileClip
from pydub import AudioSegment

from app.database.database import DatabaseManager
from app.database.models import Task
from app.services.task_processor import TaskProcessor
from app.utils.file_utils import FileUtils
from app.utils.logging_utils import configure_logging
from config.settings import Settings

# 初始化数据库管理器
db_manager = DatabaseManager()


class WhisperService:
    """
    Whisper 服务类，用于处理音频和视频的转录和音频提取。

    Whisper service class for handling transcription and audio extraction of audio and video files.
    """

    # 初始化静态线程池，所有实例共享 | Initialize static thread pool, shared by all instances
    _executor = ThreadPoolExecutor()

    def __init__(self, model_name: str = None) -> None:
        # 配置日志记录器 | Configure logger
        self.logger = configure_logging(name=__name__)

        # 初始化 FileUtils 实例 | Initialize FileUtils instance
        self.file_utils = FileUtils(
            auto_delete=Settings.FileSettings.auto_delete,
            limit_file_size=Settings.FileSettings.limit_file_size,
            max_file_size=Settings.FileSettings.max_file_size,
            temp_dir=Settings.FileSettings.temp_files_dir
        )

        # 尝试初始化 CUDA | Try to initialize CUDA
        try:
            torch.cuda.init()
            self.logger.info("CUDA initialized successfully.")
        except Exception as e:
            self.logger.warning(f"Failed to initialize CUDA: {str(e)}")

        # 选择设备和加载模型 | Select device and load model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = Settings.WhisperSettings.model_name if model_name is None else model_name
        self.logger.info(f"Loading Whisper model '{self.model_name}' on device '{self.device}'.")
        try:
            self.model = whisper.load_model(self.model_name, device=self.device)
            self.logger.info(f"Model '{self.model_name}' loaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model '{self.model_name}': {str(e)}")
            raise RuntimeError(f"Failed to load model '{self.model_name}': {e}")

        # 初始化任务处理器 | Initialize task processor
        self.task_processor = TaskProcessor(self.model, self.file_utils, db_manager)

    async def extract_audio_from_video(
            self,
            file: UploadFile,
            sample_rate: int,
            bit_depth: int,
            output_format: str,
            background_tasks: Optional[BackgroundTasks] = None
    ):
        self.logger.debug(f"Starting audio extraction from video file: {file.filename}")

        if not file.content_type.startswith("video/"):
            self.logger.warning(f"Invalid content type: {file.content_type}")
            raise HTTPException(status_code=400, detail="File must be a video file.")

        temp_video_path = await self.file_utils.save_uploaded_file(file)
        self.logger.debug(f"Video file saved to temporary path: {temp_video_path}")
        temp_files_to_delete = [temp_video_path]

        try:
            video_clip = VideoFileClip(temp_video_path)

            temp_audio_file_name = f"{uuid.uuid4().hex}.{output_format}"
            temp_audio_path = os.path.join(self.file_utils.TEMP_DIR, temp_audio_file_name)
            wav_temp_file_name = f"{uuid.uuid4().hex}.wav"
            wav_temp_path = os.path.join(self.file_utils.TEMP_DIR, wav_temp_file_name)
            temp_files_to_delete.append(wav_temp_path)

            self.logger.info(f"Extracting audio to WAV file: {wav_temp_path}")
            video_clip.audio.write_audiofile(wav_temp_path, fps=sample_rate, nbytes=bit_depth)
            self.logger.debug(f"Audio extracted to WAV file: {wav_temp_path}")

            video_clip.close()

            if output_format == "wav":
                temp_audio_path = wav_temp_path
                self.logger.debug("Output format is WAV; using extracted WAV file directly.")
            elif output_format == "mp3":
                self.logger.info(f"Converting WAV to MP3: {temp_audio_path}")
                audio = AudioSegment.from_wav(wav_temp_path)
                audio.export(temp_audio_path, format="mp3")
                self.logger.debug(f"Audio converted to MP3: {temp_audio_path}")
                temp_files_to_delete.append(temp_audio_path)
            else:
                self.logger.warning(f"Unsupported output format: {output_format}")
                raise HTTPException(status_code=400, detail="Unsupported output format, must be 'wav' or 'mp3'.")

            if background_tasks:
                self.logger.debug("Adding temporary files to background tasks for deletion.")
                for path in temp_files_to_delete:
                    if os.path.exists(path):
                        background_tasks.add_task(self.file_utils.delete_file, path)
            else:
                self.logger.debug("No background tasks provided; deleting temporary files immediately.")
                for path in temp_files_to_delete:
                    if os.path.exists(path):
                        await self.file_utils.delete_file(path)
                        self.logger.debug(f"Deleted temporary file: {path}")

            self.logger.info(f"Returning extracted audio file: {temp_audio_path}")
            return FileResponse(
                temp_audio_path,
                media_type=f"audio/{output_format}",
                filename=f"extracted_audio.{output_format}",
            )
        except Exception as e:
            self.logger.error(f"Audio extraction failed: {str(e)}")
            for path in temp_files_to_delete:
                if os.path.exists(path):
                    await self.file_utils.delete_file(path)
                    self.logger.debug(f"Deleted temporary file after failure: {path}")
            raise HTTPException(status_code=500, detail=f"Audio extraction failed: {str(e)}")
        finally:
            if 'video_clip' in locals():
                video_clip.close()
                self.logger.debug("Video clip closed.")

    async def create_transcription_task(
            self,
            file: UploadFile,
            decode_options: dict,
            priority: str,
            request: Request
    ) -> Task:
        temp_file_path = await self.file_utils.save_uploaded_file(file)
        self.logger.debug(f"Audio file saved to temporary path: {temp_file_path}")

        duration = await self.get_audio_duration(temp_file_path)

        async with db_manager.get_session() as session:
            task = Task(
                file_path=temp_file_path,
                file_name=file.filename,
                file_size_bytes=os.path.getsize(temp_file_path),
                decode_options=decode_options,
                duration=duration,
                priority=priority
            )
            session.add(task)
            await session.commit()
            task_id = task.id
            # 设置任务输出链接 | Set task output URL
            task.output_url = f"{request.url_for('get_task_result')}?task_id={task_id}"
            await session.commit()

        self.logger.info(f"Created transcription task with ID: {task_id}")
        return task

    async def get_audio_duration(self, temp_file_path):
        self.logger.debug(f"Getting duration of audio file: {temp_file_path}")
        audio = await asyncio.get_running_loop().run_in_executor(
            WhisperService._executor, lambda: AudioSegment.from_file(temp_file_path)
        )
        duration = len(audio) / 1000.0
        self.logger.debug(f"Audio file duration: {duration:.2f} seconds")
        return duration

    def start_task_processor(self):
        """启动任务处理器 | Start the task processor"""
        self.task_processor.start()

    def stop_task_processor(self):
        """停止任务处理器 | Stop the task processor"""
        self.task_processor.stop()

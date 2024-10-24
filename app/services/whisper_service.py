import os
import tempfile
from fastapi import UploadFile, HTTPException
import whisper
import logging
import torch
import aiofiles
from pydub import AudioSegment
from fastapi.responses import FileResponse

device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "large-v3"
model = whisper.load_model(model_name, device=device)

print(f"Using device: {device} and model: {model_name} for transcribing audio.")

TEMP_DIR = os.path.join(os.getcwd(), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)
print(f"Temporary directory created at: {TEMP_DIR}")


async def save_uploaded_file(file: UploadFile):
    file_path = os.path.join(TEMP_DIR, file.filename)
    try:
        async with aiofiles.open(file_path, "wb") as temp_file:
            await temp_file.write(await file.read())
        return file_path
    except Exception as e:
        logging.error(f"Failed to save file: {str(e)}")
        raise HTTPException(status_code=500, detail="文件保存失败")


def delete_file(file_path):
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        logging.debug(f"File deleted at: {file_path}")


async def transcribe_audio(
        file: UploadFile,
        speed_multiplier: float = 1.0,
        **decode_options
) -> dict:
    temp_file_path = await save_uploaded_file(file)
    try:
        if speed_multiplier != 1.0:
            audio = AudioSegment.from_file(temp_file_path)
            audio = audio.speedup(playback_speed=speed_multiplier)
            temp_fast_path = temp_file_path.replace(".mp3", "_fast.mp3")
            audio.export(temp_fast_path, format="mp3")
            temp_file_path = temp_fast_path

        result = model.transcribe(temp_file_path, **decode_options)
        return result
    except Exception as e:
        logging.error(f"Audio processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="音频处理失败")
    finally:
        delete_file(temp_file_path)


async def extract_audio_from_video(file: UploadFile, sample_rate: int, bit_depth: int, output_format: str):
    if file.content_type != "video/mp4":
        raise HTTPException(status_code=400, detail="仅支持 MP4 格式的视频文件。")
    temp_video_path = await save_uploaded_file(file)
    try:
        from moviepy.editor import VideoFileClip
        video_clip = VideoFileClip(temp_video_path)
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_format}")
        try:
            if output_format == "wav":
                video_clip.audio.write_audiofile(temp_audio_file.name, fps=sample_rate, nbytes=bit_depth)
            elif output_format == "mp3":
                wav_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                video_clip.audio.write_audiofile(wav_temp_file.name, fps=sample_rate, nbytes=bit_depth)
                audio = AudioSegment.from_wav(wav_temp_file.name)
                audio.export(temp_audio_file.name, format="mp3")
                os.remove(wav_temp_file.name)
            else:
                raise HTTPException(status_code=400, detail="不支持的音频格式，仅支持 'wav' 和 'mp3'。")

            return FileResponse(temp_audio_file.name, media_type=f"audio/{output_format}",
                                filename=f"extracted_audio.{output_format}")
        finally:
            video_clip.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音频提取失败: {e}")
    finally:
        delete_file(temp_video_path)

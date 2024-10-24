from pydantic import BaseModel
from typing import Optional


class TranscribeRequest(BaseModel):
    temperature: float = 0.0
    verbose: bool = False
    compression_ratio_threshold: float = 2.4
    logprob_threshold: float = -1.0
    no_speech_threshold: float = 0.6
    condition_on_previous_text: bool = True
    initial_prompt: str = None
    word_timestamps: bool = False
    prepend_punctuations: str = "\"'“¿([{-"
    append_punctuations: str = "\"'.。,，!！?？:：”)]}、"
    clip_timestamps: str = "0"
    hallucination_silence_threshold: float = None


from dataclasses import dataclass


@dataclass
class Settings:

    # FastAPI settings
    class FastAPISettings:
        title: str = "Whisper Speech to Text API"
        description: str = "An open source Speech-to-Text API. The project is based on OpenAI's Whisper model and uses the asynchronous features of FastAPI to efficiently wrap it and support more custom functions."
        version: str = "1.0.0"
        docs_url: str = "/"
        debug: bool = False
        ip: str = "0.0.0.0"
        port: int = 80

    # Database settings
    class DatabaseSettings:
        url: str = "sqlite+aiosqlite:///tasks.db"
    
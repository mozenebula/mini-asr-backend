from dataclasses import dataclass


@dataclass
class Settings:

    # FastAPI 设置 | FastAPI settings
    class FastAPISettings:
        # 项目名称 | Project name
        title: str = "Whisper Speech to Text API"
        # 项目描述 | Project description
        description: str = "An open source Speech-to-Text API. The project is based on OpenAI's Whisper model and uses the asynchronous features of FastAPI to efficiently wrap it and support more custom functions."
        # 项目版本 | Project version
        version: str = "1.0.0"
        # Swagger 文档 URL | Swagger docs URL
        docs_url: str = "/"
        # 是否开启 debug 模式 | Whether to enable debug mode
        debug: bool = False
        # FastAPI 服务 IP | FastAPI service IP
        ip: str = "0.0.0.0"
        # FastAPI 服务端口 | FastAPI service port
        port: int = 80

    # 数据库设置 | Database settings
    class DatabaseSettings:
        # 数据库 URL | Database URL
        url: str = "sqlite+aiosqlite:///tasks.db"

    # Whisper 设置 | Whisper settings
    class WhisperSettings:
        # 模型名称 | Model name
        model_name: str = "large-v3"

    # 文件设置 | File settings
    class FileSettings:
        # 是否自动删除临时文件 | Whether to automatically delete temporary files
        auto_delete: bool = True
        # 是否限制上传文件大小 | Whether to limit the size of uploaded files
        limit_file_size: bool = True
        # 最大上传文件大小（字节）| Maximum upload file size (bytes)
        max_file_size: int = 2147483648
        # 临时文件目录 | Temporary file directory
        temp_files_dir: str = "./temp_files"
        # 是否在处理后删除临时文件 | Whether to delete temporary files after processing
        delete_temp_files_after_processing: bool = True

    
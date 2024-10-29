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
        # 自动重载 | Auto reload
        reload: bool = False
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
        # Whisper同时处理的最大任务数，数字越大，资源占用越高，可能会导致性能下降 | The maximum number of tasks Whisper processes at the same time. The larger the number, the higher the resource consumption, which may lead to performance degradation
        MAX_CONCURRENT_TASKS: int = 1
        # 检查任务状态的时间间隔（秒） | Time interval for checking task status (seconds)
        TASK_STATUS_CHECK_INTERVAL: int = 3

    # 文件设置 | File settings
    class FileSettings:
        # 是否自动删除临时文件 | Whether to automatically delete temporary files
        auto_delete: bool = True
        # 是否限制上传文件大小 | Whether to limit the size of uploaded files
        limit_file_size: bool = True
        # 最大上传文件大小（字节）| Maximum upload file size (bytes)
        max_file_size: int = 2 * 1024 * 1024 * 1024
        # 临时文件目录 | Temporary file directory
        temp_files_dir: str = "./temp_files"
        # 是否在处理后删除临时文件 | Whether to delete temporary files after processing
        delete_temp_files_after_processing: bool = True

    # 日志设置 | Log settings
    class LogSettings:
        # 日志级别 | Log level
        """
        CRITICAL = 50
        FATAL = CRITICAL
        ERROR = 40
        WARNING = 30
        WARN = WARNING
        INFO = 20
        DEBUG = 10
        NOTSET = 0
        """
        level: int = 10
        # 日志文件目录 | Log file directory
        log_dir: str = "./log_files"
        # 日志文件前缀 | Log file prefix
        log_file_prefix: str = "app"
        # 日志文件编码 | Log file encoding
        encoding: str = "utf-8"
        # 日志文件备份数 | Log file backup count
        backup_count: int = 7
        # 日志文件切割时间 | Log file cutting time
        when: str = "midnight"
        # 日志文件切割间隔(天) | Log file cutting interval (days)
        interval: int = 1
    
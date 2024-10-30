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

from typing import Optional


class Settings:
    # FastAPI 设置 | FastAPI settings
    class FastAPISettings:
        # 项目名称 | Project name
        title: str = "Whisper Speech to Text API"
        # 项目描述 | Project description
        description: str = "An open source Speech-to-Text API. The project is based on OpenAI's Whisper model and uses the asynchronous features of FastAPI to efficiently wrap it and support more custom functions."
        # 项目版本 | Project version
        version: str = "1.0.1"
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

    # Whisper 服务类设置 | Whisper service class settings
    class WhisperServiceSettings:
        # 模型最大并发任务数，由于模型不是线程安全的，当并发大于1时，模型池会创建相同数量的模型实例，设置过大会造成性能问题以及未知错误！！！
        # The maximum number of concurrent tasks for the model.
        # Since the model is not thread-safe, when the concurrency is greater than 1,
        # the model pool will create the same number of model instances.
        # Setting it too large will cause performance problems and unknown errors!!!
        MAX_CONCURRENT_TASKS: int = 3
        # 检查任务状态的时间间隔（秒），如果设置过小可能会导致数据库查询频繁，设置过大可能会导致任务状态更新不及时。
        # Time interval for checking task status (seconds). If set too small, it may cause frequent database queries.
        TASK_STATUS_CHECK_INTERVAL: int = 3

    # OpenAI Whisper 设置 | OpenAI Whisper settings
    class OpenAIWhisperSettings:
        # 模型名称 | Model name
        openai_whisper_model_name: str = "large-v3"
        # 设备名称，如 "cpu" 或 "cuda", 为 None 时自动选择 | Device name, such as "cpu" or "cuda", automatically selected when None
        openai_whisper_device: Optional[str] = None
        # 模型下载根目录 | Model download root directory
        openai_whisper_download_root: Optional[str] = None
        # 是否在内存中加载模型 | Whether to load the model in memory
        openai_whisper_in_memory: bool = False

    # Faster Whisper 设置 | Faster Whisper settings
    class FasterWhisperSettings:
        # 模型名称 | Model name
        faster_whisper_model_size_or_path: str = "large-v3"
        # 设备名称，如 "cpu" 或 "cuda", 为 'auto' 时自动选择 | Device name, such as "cpu" or "cuda", automatically selected when 'auto'
        faster_whisper_device: str = "auto"
        # 设备ID，当 faster_whisper_device 为 "cuda" 时有效 | Device ID, valid when faster_whisper_device is "cuda"
        faster_whisper_device_index: int = 0
        # 模型推理计算类型 | Model inference calculation type
        faster_whisper_compute_type: str = "float16"
        # 模型使用的CPU线程数，设置为 0 时使用所有可用的CPU线程 | The number of CPU threads used by the model, set to 0 to use all available CPU threads
        faster_whisper_cpu_threads: int = 0
        # 模型worker数 | Model worker count
        faster_whisper_num_workers: int = 1
        # 模型下载根目录 | Model download root directory
        faster_whisper_download_root: Optional[str] = None

    # 异步模型池设置 | Asynchronous model pool settings
    class AsyncModelPoolSettings:
        # 引擎名称 | Engine name
        # 目前只支持 "openai_whisper" 和 "faster_whisper" | Currently only supports "openai_whisper" and "faster_whisper"
        engine: str = "faster_whisper"

        # 最小的模型池大小 | Minimum model pool size
        min_size: int = 1

        # 最大的模型池大小，建议跟 WhisperSettings.MAX_CONCURRENT_TASKS 保持一致
        # Maximum model pool size, it is recommended to be consistent with WhisperSettings.MAX_CONCURRENT_TASKS
        @classmethod
        def get_max_size(cls) -> int:
            return Settings.WhisperServiceSettings.MAX_CONCURRENT_TASKS

        # 是否在模型池初始化时以最大并发任务数创建模型实例 | Whether to create model instances with the maximum number of concurrent tasks when the model pool is initialized
        @classmethod
        def create_with_max_concurrent_tasks(cls) -> bool:
            return True if cls.get_max_size() > 1 else False

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

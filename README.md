<div align="center">
<a href="https://github.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API" alt="logo" ><img src="https://raw.githubusercontent.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API/refs/heads/main/github/logo/logo.jpg" width="150"/></a>
</div>
<h1 align="center">Fast-Powerful-Whisper-AI-Services-API</h1>

<div align="center">

[English](./README.md) | [简体中文](./README-ZH.md)

<hr>
</div>

<div align="left">

🚀 The vision of 「 **[Fast-Powerful-Whisper-AI-Services-API](https://github.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API)** 」is to create a powerful, ready-to-use [Whisper](https://github.com/openai/whisper) service API, designed for high performance, scalability, and distributed processing requirements. Built around a producer-consumer model, it is ideal for large-scale, highly efficient automatic speech recognition scenarios. This project leverages the OpenAI Whisper model and the Faster Whisper model, which delivers faster inference with nearly equivalent accuracy. It supports high-quality multilingual transcription and translation tasks. With an integrated crawler module, it easily processes videos from social media platforms like Douyin and TikTok, creating tasks with just a link input.

The system efficiently manages resource scheduling and task management through an asynchronous model pool solution, supporting parallel computation on multiple GPUs for fully localized, scalable, and reliable operations. Additionally, the project plans to support a flexible custom component and workflow design, allowing users to define complex multi-step workflows via JSON files or extend functionality by writing custom components in Python. Built-in modules for high-performance asynchronous HTTP, file I/O, and database operations enable users to develop custom services or task processors, with future plans to integrate with LLM APIs like ChatGPT to realize a complete workflow from automatic speech recognition to natural language processing and analysis.

</div>

## 🌟 Key Features

* **Asynchronous Design** : Built on Python 3.11’s asyncio capabilities, all modules are asynchronous, enabling efficient request handling and enhancing overall system stability and high concurrency.
* **Built-in Document UI** : Leveraging FastAPI’s auto-generated OpenAPI JSON, the project includes an interactive Swagger UI for visual API testing in the browser. Swagger UI provides bilingual descriptions in English and Chinese with default parameter settings, enabling quick start testing for users.
* **High Accuracy** : The latest `large-v3` model ensures accurate output, and Faster Whisper significantly reduces inference time while maintaining high accuracy.
* **Distributed Deployment** : The project can access and store tasks in a shared database and plans seamless integration with Kafka, achieving a harmonious integration of FastAPI and Kafka for building real-time, intelligent Web APIs.
* **Asynchronous Model Pool** : Implements an efficient asynchronous AI model pool that supports multi-instance concurrent processing for OpenAI Whisper and Faster Whisper models under thread-safe conditions. In CUDA-accelerated, multi-GPU environments, intelligent loading mechanisms dynamically assign models to GPUs, balancing load and optimizing task processing. Note: Concurrency is unavailable on single-GPU setups.
* **Asynchronous Database** : Supports MySQL and SQLite databases. It can run locally without MySQL, as SQLite allows for quick setup. When using MySQL, it facilitates distributed computing with multiple nodes accessing the same database for tasks.
* **Asynchronous Web Crawlers** : Equipped with data crawler modules for multiple platforms, currently supporting `Douyin` and `TikTok`. By simply entering the video link, users can quickly process media for speech recognition, with plans for more social media platform support in the future.
* **Workflow and Component Design (Pending)** : With a focus on Whisper transcription tasks, the project will support a highly customizable workflow system. Users can define components, task dependencies, and execution orders in JSON files or write custom components in Python, facilitating complex multi-step processing.
* **Event-Driven Intelligent Workflow (Pending)** : The workflow system supports event-driven triggers, including time-based, manual, or crawler module auto-triggers. More than single-task processing, workflows will offer intelligent, automated control with conditional branching, task dependencies, dynamic parameter passing, and retry strategies.

## 💫 Suitable Scenarios

* **Media Data Processing** : Ideal for large-scale speech-to-text processing, such as transcription, analysis, translation, and subtitle generation of online or local media files.
* **Automated Workflow** : While the project doesn’t yet include workflows, it can integrate with other platforms' workflow systems through the API, enabling complex automated task execution for scenarios requiring multi-step processing and conditional control.
* **Dynamic Data Collection** : Combined with asynchronous crawler modules, the system can automatically collect and process online data, storing processed results for analysis.
* **Distributed Computing Utilization** : When leveraging distributed, fragmented computing resources, the gateway-based structure enables efficient utilization of dispersed computing power.

## 🚩 Implemented Features

* **Create Task** : Supports media file upload (`file_upload`) or specifying a media file link (`file_url`) as the data source for the task, with configurable parameters for fine-grained task control.
* **Set Task Type** : Users can set the task type by adjusting the `task_type` parameter. Currently supports media file transcription (`transcribe`) and automatic translation (`translate`).
* **Set Task Priority** : Users can assign task priority via the `priority` parameter, supporting three priority levels: (`high`, `normal`, `low`).
* **Task Callback Notification** : Users can specify a `callback_url` to receive task completion data. Upon task completion, an HTTP POST request is sent to the specified address, and callback statuses are logged in the database for review.
* **Multi-Platform Support** : Users can create Douyin and TikTok tasks through respective interfaces, or manually specify a video link with the `platform` parameter to mark the platform name.
* **Configure Whisper Parameters** : Users can customize the model’s inference by setting decoding parameters. Supported parameters include (`language`, `temperature`, `compression_ratio_threshold`, `no_speech_threshold`, `condition_on_previous_text`, `initial_prompt`, `word_timestamps`, `prepend_punctuations`, `append_punctuations`, `clip_timestamps`, `hallucination_silence_threshold`).
* **Task Querying** : Users can query the task list with various filters, including task status, priority, creation time, language, and engine name. This endpoint supports pagination, with `limit` and `offset` parameters controlling records per page.
* **Delete Task** : Users can delete tasks by `task_id`, permanently removing task data.
* **Get Task Results** : Users can retrieve results for a specified task by `task_id`.
* **Extract Audio from Video** : Allows users to extract audio from uploaded video files, supporting sample rate (`sample_rate`), bit depth (`bit_depth`), and output format (`output_format`) settings.
* **Generate Subtitle File** : Users can generate subtitles for a task by specifying the `task_id` and output format (`output_format`). Currently supports (`srt`) and (`vtt`) subtitle file formats.
* **Create TikTok Task** : Users can create tasks by crawling TikTok videos through a video link.
* **Create Douyin Task** : Users can create tasks by crawling Douyin videos through a video link.

## 📸 Project Screenshots

![2024_07_56_AM.png](https://github.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API/blob/main/github/screenshots/2024_07_56_AM.png?raw=true)

## 🚀 Quick Deployment

Follow these steps to deploy the project quickly.

1. **Clone the Project** : Make sure `git` is installed, then open the console or terminal on your computer to run the following command:
   
   ```bash
   git clone https://github.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API.git
   ```
2. **Python Environment** : Recommended Python version is `3.12` or `>=3.8`.
3. **Install FFmpeg** : The project uses [FFmpeg](https://www.ffmpeg.org/) for audio and video encoding and decoding. Install FFmpeg based on your OS:

- **Ubuntu or Debian**
  ```bash
  sudo apt update && sudo apt install ffmpeg
  ```
- **Arch Linux**
  ```bash
  sudo pacman -S ffmpeg
  ```
- **MacOS (Homebrew)**
  ```bash
  brew install ffmpeg
  ```
- **Windows (Chocolatey - Method 1)**
  ```bash
  choco install ffmpeg
  ```
- **Windows (Scoop - Method 2)**
  ```bash
  scoop install ffmpeg
  ```

4. **Install CUDA** : The project uses [CUDA](https://developer.nvidia.com/cuda-toolkit) for GPU-accelerated inference. Skip this step if using only the CPU.

* Download and install the appropriate version for your system:
* [CUDA Downloads](https://developer.nvidia.com/cuda-downloads)

5. **Install PyTorch with CUDA Support** : Ensure the CUDA Toolkit version matches your GPU.

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

6. **Install Project Dependencies** : Navigate to the project directory and install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
7. **Modify Default Configurations** : Most settings are customizable. Review the default configuration file at the following link. Changes to the configuration file may require a project restart.

* Default configuration file: [settings.py](https://github.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API/blob/main/config/settings.py)

8. **Start the Project** : Ensure you are in the root project directory.

- Start the API:
  ```bash
  python3 start.py
  ```
- Access the API documentation in your browser at [http://127.0.0.1/](http://127.0.0.1/).

## ⚗️ Tech Stack

* **[OpenAI Whisper](https://github.com/openai/whisper)** - Speech recognition model
* **[Faster Whisper](https://github.com/SYSTRAN/faster-whisper)** - Faster speech recognition model
* **[ffmpeg](https://ffmpeg.org/)** - Audio/video format conversion
* **[torch](https://pytorch.org/)** - Deep learning framework
* **[FastAPI](https://github.com/fastapi/fastapi)** - High-performance API framework
* **[HTTPX](https://www.python-httpx.org/)** - Asynchronous HTTP client
* **[aiofile](https://github.com/Tinche/aiofiles)** - Asynchronous file operations
* **[aiosqlite](https://github.com/omnilib/aiosqlite)** - Asynchronous database operations
* **[aiomysql](https://github.com/aio-libs/aiomysql)** - Asynchronous database operations
* **[moviepy](https://github.com/Zulko/moviepy)** - Video editing
* **[pydub](https://github.com/jiaaro/pydub)** - Audio editing

## 🗃️ Project Structure

```
📂 Fast-Powerful-Whisper-AI-Services-API/
├── 📁 app/
│   ├── 📁 api/ -> API layer containing models and routes
│   │   ├── 📁 models/
│   │   │   └── 📄 APIResponseModel.py -> Defines API response models
│   │   ├── 📁 routers/
│   │   │   ├── 🔍 health_check.py -> Health check endpoint
│   │   │   ├── 📝 whisper_tasks.py -> Routes for Whisper tasks
│   │   │   └── 🔄 work_flows.py -> Routes for workflow management
│   │   └── 📄 router.py -> Main router module
│   ├── 🕸️ crawlers/ -> Modules for web crawling
│   │   ├── 📁 platforms/
│   │   │   ├── 📁 douyin/
│   │   │   │   ├── 🐛 abogus.py -> (`・ω・´) Whats This?
│   │   │   │   ├── 🚀 crawler.py -> Douyin data crawler
│   │   │   │   ├── 📡 endpoints.py -> API endpoints for Douyin crawler
│   │   │   │   ├── 🧩 models.py -> Models for Douyin data
│   │   │   │   └── 🛠️ utils.py -> Utility functions for Douyin crawler
│   │   │   │   └── 📘 README.md -> Douyin module documentation
│   │   │   └── 📁 tiktok/
│   │   │       ├── 🚀 crawler.py -> TikTok data crawler
│   │   │       ├── 📡 endpoints.py -> API endpoints for TikTok crawler
│   │   │       ├── 🧩 models.py -> Models for TikTok data
│   │   │       └── 📘 README.md -> TikTok module documentation
│   ├── 💾 database/ -> Database models and management
│   │   ├── 🗄️ DatabaseManager.py -> Handles database connections
│   │   ├── 📂 TaskModels.py -> Task-related database models
│   │   └── 📂 WorkFlowModels.py -> Workflow-related database models
│   ├── 🌐 http_client/ -> HTTP client setup
│   │   ├── ⚙️ AsyncHttpClient.py -> Asynchronous HTTP client
│   │   └── ❗ HttpException.py -> Custom HTTP exceptions
│   ├── 🤖 model_pool/ -> Model pooling and management
│   │   └── 🧠 AsyncModelPool.py -> Asynchronous model pool manager
│   ├── 🔄 processors/ -> Task and workflow processors
│   │   ├── 📋 task_processor.py -> Processes Whisper tasks
│   │   └── 🛠️ workflow_processor.py -> Processes workflows
│   ├── 🛎️ services/ -> Service layer for API functions
│   │   ├── 📲 callback_service.py -> Handles callbacks
│   │   ├── 🔄 workflow_service.py -> Workflow handling services
│   │   └── 🗣️ whisper_service.py -> Whisper model-related services
│   ├── 🧰 utils/ -> Utility functions
│   │   ├── 📂 file_utils.py -> File operations and management
│   │   └── 🔍 logging_utils.py -> Logging utilities
│   ├── ⚙️ workflows/ -> Workflow components
│   │   └── 🧩 components/
│   │       ├── 🛠️ base_component.py -> Base workflow component
│   │       ├── 📄 component_a.py -> Custom workflow component A
│   │       └── 📄 component_b.py -> Custom workflow component B
│   └── 🚀 main.py -> Application entry point
├── ⚙️ config/
│   └── 🛠️ settings.py -> Configuration file
├── 📁 temp_files/ -> Temporary files folder
│   └── 📂 -> Default TEMP Files Folder
├── 📁 log_files/ -> Log files folder
│   └── 📂 -> Default LOG Files Folder
└── 📂 WhisperServiceAPI.db -> Default SQLite DB File
└── 📄 requirements.txt -> Python package requirements
└── 📝 start.py -> Run to start the API
```

## 🛠️ Usage Guide

* Navigate to the project directory and use the following command to start the API service:
  * `python3 start.py`
* You can then access `http://localhost` to view the API documentation and test the endpoints on the web.

## 🍱 API Usage Examples (CURL Format)

* Adding a TikTok task

```curl
curl -X 'POST' \
  'http://127.0.0.1/api/tiktok/video_task' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'priority=normal&prepend_punctuations=%22'\''%E2%80%9C%C2%BF(%5B%7B-&no_speech_threshold=0.6&clip_timestamps=0&url=https%3A%2F%2Fwww.tiktok.com%2F%40taylorswift%2Fvideo%2F7359655005701311786&word_timestamps=false&platform=tiktok&temperature=0.8%2C1.0&task_type=transcribe&callback_url=&hallucination_silence_threshold=0&language=&condition_on_previous_text=true&compression_ratio_threshold=1.8&append_punctuations=%22'\''.%E3%80%82%2C%EF%BC%8C!%EF%BC%81%3F%EF%BC%9F%3A%EF%BC%9A%E2%80%9D)%5D%7D%E3%80%81&initial_prompt='
```

- Response

```json
{
  "code": 200,
  "router": "http://127.0.0.1/api/tiktok/video_task",
  "params": {
    "language": null,
    "temperature": [
      0.8,
      1
    ],
    "compression_ratio_threshold": 1.8,
    "no_speech_threshold": 0.6,
    "condition_on_previous_text": true,
    "initial_prompt": "",
    "word_timestamps": false,
    "prepend_punctuations": "\"'“¿([{-",
    "append_punctuations": "\"'.。,，!！?？:：”)]}、",
    "clip_timestamps": "0.0",
    "hallucination_silence_threshold": null,
    "task_type": "transcribe",
    "priority": "normal",
    "callback_url": ""
  },
  "data": {
    "id": 8,
    "status": "queued",
    "callback_url": "",
    "callback_status_code": null,
    "callback_message": null,
    "callback_time": null,
    "priority": "normal",
    "engine_name": "faster_whisper",
    "task_type": "transcribe",
    "created_at": "2024-11-07T06:31:57.894804",
    "updated_at": "2024-11-07T06:31:57.894804",
    "task_processing_time": null,
    "file_path": null,
    "file_url": "https://api.tiktokv.com/aweme/v1/play/?file_id=3146fc434e4d493c93b78566726b9310&is_play_url=1&item_id=7359655005701311786&line=0&signaturev3=dmlkZW9faWQ7ZmlsZV9pZDtpdGVtX2lkLjA3YTkzYjY0ZTliOWUzMzVmN2VhODgxMTMyMDljYTJk&source=FEED&vidc=useast5&video_id=v12044gd0000cohbuanog65ltpj9jdpg",
    "file_name": null,
    "file_size_bytes": null,
    "file_duration": null,
    "language": null,
    "platform": "tiktok",
    "decode_options": {
      "language": null,
      "temperature": [
        0.8,
        1
      ],
      "compression_ratio_threshold": 1.8,
      "no_speech_threshold": 0.6,
      "condition_on_previous_text": true,
      "initial_prompt": "",
      "word_timestamps": false,
      "prepend_punctuations": "\"'“¿([{-",
      "append_punctuations": "\"'.。,，!！?？:：”)]}、",
      "clip_timestamps": "0.0",
      "hallucination_silence_threshold": null
    },
    "error_message": null,
    "output_url": "http://127.0.0.1/api/whisper/tasks/result?task_id=8",
    "result": null
  }
}
```

**When an audio or video file is included in the request body, the API will return the transcribed text result.**

## 🦺 Performance Testing

* Testing Environment and Hardware Configuration
  * CPU: 13th Gen Intel(R) Core(TM) i9-13950HX 24-core 32-thread @ 2.20 GHz
  * GPU: NVIDIA GeForce RTX 4060 Laptop GPU
  * Memory: 64GB
  * System: Windows 11

> Single Queue Test

* We use the `faster whisper` model as the engine with `CUDA` acceleration.
* The inference model used is `large-v3`.
* The asynchronous model pool’s maximum concurrency `MAX_CONCURRENT_TASKS` is set to 1.
* Using a 39-second video for testing, five requests were sent consecutively, and the total processing time for all tasks was 32 seconds.

> Concurrent Mode Testing

* To be added.

## 📝 To-Do List

* Enhance the crawler module with additional platform support.
* Improve task flow system, implementing an automated event- or time-driven workflow system.
* Add LLM support to enable further processing, such as content summarization and semantic analysis, suitable for secondary analysis or text mining.
* Optimize database structure and design, with plans to support Redis and add more fields to store more data.
* Add deployment scripts for a one-click deployment bash script to facilitate easy project setup.
* Containerize the project with Docker and add automated container build scripts.

## 🔧 Default Configuration File

```python
import os
from typing import Optional
from dotenv import load_dotenv

# 加载 .env 文件 | Load .env file
load_dotenv()


class Settings:

    # FastAPI 设置 | FastAPI settings
    class FastAPISettings:
        # 项目名称 | Project name
        title: str = "Fast-Powerful-Whisper-AI-Services-API"
        # 项目描述 | Project description
        description: str = "An open source speech-to-text API that runs completely locally. The project is based on the OpenAI Whisper model and the faster inference Faster Whisper model, and implements an asynchronous model pool, using the asynchronous features of FastAPI for efficient packaging, supporting thread-safe asynchronous task queues, asynchronous file IO, asynchronous database IO, asynchronous web crawler modules, and more custom features."
        # 项目版本 | Project version
        version: str = "1.0.3"
        # Swagger 文档 URL | Swagger docs URL
        docs_url: str = "/"
        # 是否开启 debug 模式 | Whether to enable debug mode
        debug: bool = False
        # 当检测到项目代码变动时是否自动重载项目 | Whether to automatically reload the project when changes to the project code are detected
        reload_on_file_change: bool = os.getenv("RELOAD_ON_FILE_CHANGE", True)
        # FastAPI 服务 IP | FastAPI service IP
        ip: str = "0.0.0.0"
        # FastAPI 服务端口 | FastAPI service port
        port: int = 80

    # 数据库设置 | Database settings
    class DatabaseSettings:
        # 选择数据库类型，支持 "sqlite" 和 "mysql" | Select the database type, support "sqlite" and "mysql"
        # "sqlite"：适合小规模项目单机运行，无需安装数据库，直接使用文件存储数据 | "sqlite": Suitable for small-scale projects running on a single machine, no need to install a database, directly use file storage data
        # "mysql"：适合大规模项目分布式部署，需要安装 MySQL 数据库 | "mysql": Suitable for large-scale projects distributed deployment, need to install MySQL database
        # 如果你选择 "mysql"，请确保安装了 aiomysql | If you choose "mysql", please make sure aiomysql is installed
        # 如果你选择 "sqlite"，请确保安装了 aiosqlite | If you choose "sqlite", please make sure aiosqlite is installed
        db_type: str = os.getenv("DB_TYPE", "sqlite")

        # SQLite 数据库设置 | SQLite database settings
        # 数据库名字 | Database name
        sqlite_db_name: str = os.getenv("sqlite_db_name", "WhisperServiceAPI.db")
        # 数据库 URL | Database URL
        sqlite_url: str = f"sqlite+aiosqlite:///{sqlite_db_name}"

        # MySQL 数据库设置 | MySQL database settings
        # 数据库名字 | Database name
        mysql_db_name: str = os.getenv("MYSQL_DB_NAME", "")
        # 数据库用户名 | Database username
        mysql_username: str = os.getenv("MYSQL_USERNAME", "")
        # 数据库密码 | Database password
        mysql_password: str = os.getenv("MYSQL_PASSWORD", "")
        # 数据库地址 | Database host
        mysql_host: str = os.getenv("MYSQL_HOST", "")
        # 数据库端口 | Database port
        mysql_port: int = 3306
        # 数据库 URL | Database URL
        mysql_url: str = f"mysql+aiomysql://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db_name}"

    # Whisper 服务类设置 | Whisper service class settings
    class WhisperServiceSettings:
        # Whisper 服务的最大并发任务数，设置为 1 时为单任务模式 | The maximum number of concurrent tasks for the Whisper service, set to 1 for single task mode
        # 如果你有多个 GPU，可以设置大于 1，在单一 GPU 上运行多个任务无法缩短任务时间，但可以提高任务并发度 | If you have multiple GPUs, you can set it to more than 1. Running multiple tasks on a single GPU cannot shorten the task time, but can increase the task concurrency
        MAX_CONCURRENT_TASKS: int = 1
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

        # 最大的模型池大小，如果你没有多个 GPU，建议设置为 1 | Maximum model pool size, if you don't have multiple GPUs, it is recommended to set it to 1
        # 如果你有多个 GPU，可以设置大于 1，程序会自动为每个 GPU 创建一个模型实例 | If you have multiple GPUs, you can set it to more than 1, and the program will automatically create a model instance for each GPU
        max_size: int = 1

        # 每个 GPU 最多支持的实例数量，如果你的 GPU 内存足够大，可以设置大于 1 | The maximum number of instances supported by each GPU, if your GPU memory is large enough, you can set it to more than 1
        max_instances_per_gpu: int = 1

        # 是否在模型池初始化时以最大的模型池大小创建模型实例 | Whether to create model instances with the maximum model pool size when the model pool is initialized
        init_with_max_pool_size: bool = True

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
        # 允许保存的文件类型，加强服务器安全性，为空列表时不限制 | Allowed file types, enhance server security, no restrictions when the list is empty
        allowed_file_types: list = [
            # （FFmpeg 支持的媒体文件）| (FFmpeg supported media files)
            '.3g2', '.3gp', '.aac', '.ac3', '.aiff', '.alac', '.amr', '.ape', '.asf', '.avi', '.avs', '.cavs', '.dirac',
            '.dts', '.dv', '.eac3', '.f4v', '.flac', '.flv', '.g722', '.g723_1', '.g726', '.g729', '.gif', '.gsm',
            '.h261', '.h263', '.h264', '.hevc', '.jpeg', '.jpg', '.lpcm', '.m4a', '.m4v', '.mkv', '.mlp', '.mmf',
            '.mov', '.mp2', '.mp3', '.mp4', '.mpc', '.mpeg', '.mpg', '.oga', '.ogg', '.ogv', '.opus', '.png', '.rm',
            '.rmvb', '.rtsp', '.sbc', '.spx', '.svcd', '.swf', '.tak', '.thd', '.tta', '.vc1', '.vcd', '.vid', '.vob',
            '.wav', '.wma', '.wmv', '.wv', '.webm', '.yuv',
            # （字幕文件）| (Subtitle files)
            '.srt', '.vtt',
        ]

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

    # 抖音 API 设置 | Douyin API settings
    class DouyinAPISettings:
        # Douyin Web Cookie
        web_cookie: str = os.getenv("DOUYIN_WEB_COOKIE", "")
        # Proxy
        proxy: str = os.getenv("DOUYIN_PROXY", None)
```

## 🛡️ License

This project is open-sourced under the [Apache2.0](LICENSE) license.

For commercial use and custom cooperation, please contact **Email：[evil0ctal1985@gmail.com](evil0ctal1985@gmail.com)**

## 📬 Contact

For any questions or suggestions, feel free to reach out via [issue](https://github.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API/issues).

## 🧑‍💻 Contribution Guide

We highly welcome your feedback and suggestions! Reach out through GitHub issues, or if you wish to contribute code, please fork the project and submit a pull request. We look forward to your participation! 💪

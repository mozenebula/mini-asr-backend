<div align="center">
<a href="https://github.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API" alt="logo" ><img src="https://raw.githubusercontent.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API/refs/heads/main/github/logo/logo.jpg" width="150"/></a>
</div>
<h1 align="center">Fast-Powerful-Whisper-AI-Services-API</h1>

<div align="center">

[English](./README-EN.md) | [简体中文](./README.md)

 <hr>
</div>
    
<div align="left">

🚀「**[Fast-Powerful-Whisper-AI-Services-API](https://github.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API)** 」的愿景是打造一个强大且开箱即用的 [Whisper](https://github.com/openai/whisper) 服务 API，专为高性能、高扩展性和分布式处理需求而设计，并且以生产者消费者模式为设计核心打造，理想适用于需要大规模、高效自动语音识别的场景。该项目基于 OpenAI Whisper 模型以及推理速度更快并且准确度近似的 Faster Whisper 模型，支持多语言的高质量语音转录和翻译任务，并且内置的爬虫模块可以轻松实现对抖音和TikTok等社交媒体平台的视频进行处理，只需要输入一个链接接口轻松创建任务。

本系统通过异步模型池方案实现了高效的资源调度与任务管理，并且异步模型池支持使用多个GPU进行并行计算，提供完全本地化、高拓展性，且可靠的解决方案。此外，项目计划实现一套灵活的自定义组件和工作流设计，使用户可以通过 JSON 文件定义复杂的多步骤任务流，或通过 Python 编写自定义组件，扩展功能。内置高性能的异步 HTTP 模块，异步文件IO模块，异步数据库模块，用户可以利用这些模块编写自己的服务或任务处理器来拓展业务，未来计划与ChatGPT等LLM API进行接入，实现自动语音识别到自然语言处理和分析的的完整工作流程。
    
</div>

## 🌟 项目特色

* **异步设计** ：基于Python 3.11的 asyncio 异步特性，所有模块都使用异步特性进行编写，实现请求的高效处理，提升整体系统的稳定性和高并发能力。
* **自带文档UI**：得益于FastAPI自动生成的OpenAPI JSON，本项目自带一个可交互的Swagger UI用于在浏览器中可视化的测试接口，并且接口Swagger UI中带有详细的中文+英文双语说明和默认参数设置，用户可以快速的上手测试。
* **高准确率**：使用最新的`large-v3`模型确保输出的准确率，并且得益于Faster Whisper的加持，在保证准确率的情况下可以极大地缩短推理所需的时间。
* **分布式部署**：本项目可以从同一个数据库中获取任务以及存储任务结果，未来计划与Kafka无缝对接，实现FastAPI与Kafka的完美交响：构建实时更新的智能Web API
* **异步模型池** ：本项目实现了一个高效的异步AI模型池，在线程安全的情况下支持 OpenAI Whisper 和 Faster Whisper 模型的多实例并发处理场景，在支持CUDA加速且拥有多个GPU的场景中，通过智能加载机制可以将多个模型智能的加载在多个GPU上，然后模型实例间自动分配任务，确保任务处理速度和系统负载均衡，但是在单一GPU场景下无法提供并发功能。
* **异步数据库**：本项目支持使用MySQL和SQLite作为数据库，在本机运行时无需安装和配置MySQL，使用SQLite即可快速运行项目，如果使用MySQL则可以更好的配合分布式计算，多个节点使用同一个数据库作为任务源。
* **异步网络爬虫**：本项目内置了多个平台的数据爬虫模块，当前支持`抖音`、`TikTok`，用户只需要输入对应的视频链接即可快速的对媒体进行语音识别，并且未来计划支持更多社交媒体平台。
* **工作流与组件化设计（待实现）** ：围绕 Whisper 转录任务，项目支持高度自定义的工作流系统。用户可以通过 JSON 文件定义组件、任务依赖和执行顺序，甚至可以使用 Python 编写自定义组件，灵活扩展系统功能，轻松实现复杂的多步骤处理流程。
* **事件驱动的智能工作流（待实现）** ：工作流系统支持事件触发，可以基于时间、手动触发，或由爬虫模块自动触发。相比单一任务，工作流更加智能，支持条件分支、任务依赖、动态参数传递和重试策略，为用户提供更高的自动化和可控性。

## 💫 适用场景

* **媒体数据处理** ：适用于需要大规模语音转文本处理的场景，比如网络或本地的媒体文件转录，分析，翻译，生成字幕等应用。
* **自动化工作流** ：虽然目前项目本身没有实现工作流，但是可以通过API于其他平台的任务流系统进行接入，通过事件驱动的工作流，轻松实现复杂任务的自动化执行，适合需要多步骤处理和条件控制的业务逻辑。
* **动态数据采集** ：结合异步爬虫模块，系统可自动采集和处理来自网络的数据，并且存储处理完成后的数据。
* **利用分布算力**：在多个分布的零散算力下，可以使用网关的形式将分散的算力进行有效利用。


## 🚩 已实现的功能：

- **创建任务：** 支持上传媒体文件（`file_upload`）或指定媒体文件链接（`file_url`）作为任务的数据源，并且设置一系列参数更加细粒的处理任务，见下文。
- **设置任务类型：** 用户可以通过修改（`task_type`）参数设置任务类型，当前支持媒体文件转文本（`transcribe`）或自动翻译（`translate`）
- **设置任务处理优先级：** 用户可以通过 `priority` 参数指定任务优先级，目前支持三种优先级（`high`, `normal`, `low`）
- **任务回调通知：** 用户在创建任务时可以指定 `callback_url` 作为任务完成后的数据接收地址，任务处理完成后会向目标地址发送一个HTTP POST请求将任务的结果数据传递到指定服务器，并且回调状态会被记录在数据库中方便审查。
- **多平台支持：** 用户可以在对应接口中创建抖音任务、TikTok任务，也可以手动使用视频链接并且手动使用`platform`参数标记平台名称。
- **设置Whisper参数：** 用户可以手动设置解码参数来修改模型的推理过程，当前支持多种参数（`language`，`temperature`, `compression_ratio_threshold`, `no_speech_threshold`, `condition_on_previous_text`, `initial_prompt`, `word_timestamps`, `prepend_punctuations`, `append_punctuations`, `clip_timestamps`, `hallucination_silence_threshold`）
- **查询任务**：用户可以根据多种筛选条件查询任务列表，包括任务状态、优先级、创建时间、语言、引擎名称等信息，该接口适用于分页查询，并且通过 limit 和 offset 参数控制每页显示的记录数，支持客户端逐页加载数据。
- **删除任务**： 用户可以根据任务ID删除任务，删除后任务数据将被永久删除。
- **获取任务结果**：用户可以根据任务ID获取指定任务的结果信息。
- **提取视频的音频**：运行用户上传文件来从视频文件中提取音频，支持设置采样率（`sample_rate`），位深度（`bit_depth`），输出格式（`output_format`）。
- **生成字幕文件**：用户可以通过指定的任务ID来生成指定任务的字幕，并且支持指定输出格式（`output_format`），当前支持（`srt`）以及（`vtt`）作为字幕文件格式。
- **创建TikTok任务**：用户可以通过 TikTok 视频链接爬取视频并创建任务。
- **创建抖音任务**：用户可以通过抖音视频链接爬取视频并创建任务。

## 📸 项目截图


![2024_07_56_AM.png](https://github.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API/blob/main/github/screenshots/2024_07_56_AM.png?raw=true)

## 🚀 快速部署

1. **克隆本项目**： 确保你的电脑上正确安装了`git`，然后打开你电脑上的控制台或终端来执行下方的命令
    - 下载项目文件：
        ```bash
        git clone https://github.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API.git
        ```
2. **Python 环境**：推荐使用Python 版本 `3.12` 或确保 Python 版本 >= `3.8`。
3. **安装 FFmpeg**：本项目使用 [FFmpeg](https://www.ffmpeg.org/) 作为音视频编解码工具，你可以根据你的系统类型来执行下方对应的命令来安装。
    - **Ubuntu or Debian 系统**  
        ```bash
        sudo apt update && sudo apt install ffmpeg
        ```
    - **Arch Linux 系统**
        ```bash
        sudo pacman -S ffmpeg
        ```
    - **MacOS 系统 (Homebrew)**
        ```bash
        brew install ffmpeg
        ```
    - **Windows 系统 (Chocolatey - 方法一)**
        ```bash
        choco install ffmpeg
        ```
    - **Windows 系统 (Scoop - 方法二)**
        ```bash
        scoop install ffmpeg
        ```
4. **安装 CUDA**：本项目使用 [CUDA](https://developer.nvidia.com/cuda-toolkit) 利用 GPU 进行推理加速，如果你想仅使用 CPU 来进行推理则可跳过这部分。
    - 请根据你的系统下载并安装对应版本的 Cuda-Toolkit
    - [https://developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads)
5. **安装支持CUDA的PyTorch**: 确保正确安装了匹配你的GPU的CUDA Toolkit。
    - 使用控制台或终端执行下方的命令：
        ```bash
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
        ```
6. **安装项目依赖**: 确保你在项目的目录中，这一步将把所需要的依赖库安装到本地。
    - 使用控制台或终端执行下方的命令：
        ```bash
        pip install -r requirements.txt
        ```
7. **修改项目的默认配置**：本项目的大多数设置都是可以修改的，你可以在下面的链接中查看默认的项目配置，默认的配置是不会自动重载项目的，你也可以在配置中开启自动重载，修改配置文件后建议重启一次服务。
    - 默认配置文件链接：
    - https://github.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API/blob/main/config/settings.py
8. **启动项目**：确保你在项目的根目录下。
    - 启动API：
        ```bash
        python3 start.py
        ```
    - 在浏览器上查看接口文档
    - 项目默认运行在 http://127.0.0.1/

## ⚗️ 技术栈

* **[OpenAI Whisper](https://github.com/openai/whisper)** - 语音识别模型
* **[Faster Whisper](https://github.com/SYSTRAN/faster-whisper)** - 更快速的语音识别模型
* **[ffmpeg](https://ffmpeg.org/)** - 音视频格式转换
* **[torch](https://pytorch.org/)** - 深度学习框架
* **[FastAPI](https://github.com/fastapi/fastapi)** - 高性能 API 框架
* **[HTTPX](https://www.python-httpx.org/)** - 异步 HTTP 框架
* **[aiofile](https://github.com/Tinche/aiofiles)** - 异步文件操作
* **[aiosqlite](https://github.com/omnilib/aiosqlite)** - 异步数据库操作
* **[aiosmysql](https://github.com/aio-libs/aiomysql)** - 异步数据库操作
* **[moviepy](https://github.com/Zulko/moviepy)** - 视频编辑
* **[pydub](https://github.com/jiaaro/pydub)** - 音频编辑

## 🗃️ 项目结构
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

## 🛠️ 使用指南

- 切换到项目目录，使用下面的命令启动API服务：
- `python3 start.py`
- 随后你可以访问`http://localhost`来查看接口文档，并且在网页上测试。

## 🍱 接口使用示例（CURL格式）

- 添加一个TikTok任务

```curl
curl -X 'POST' \
  'http://127.0.0.1/api/tiktok/video_task' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'priority=normal&prepend_punctuations=%22'\''%E2%80%9C%C2%BF(%5B%7B-&no_speech_threshold=0.6&clip_timestamps=0&url=https%3A%2F%2Fwww.tiktok.com%2F%40taylorswift%2Fvideo%2F7359655005701311786&word_timestamps=false&platform=tiktok&temperature=0.8%2C1.0&task_type=transcribe&callback_url=&hallucination_silence_threshold=0&language=&condition_on_previous_text=true&compression_ratio_threshold=1.8&append_punctuations=%22'\''.%E3%80%82%2C%EF%BC%8C!%EF%BC%81%3F%EF%BC%9F%3A%EF%BC%9A%E2%80%9D)%5D%7D%E3%80%81&initial_prompt='
```

- 响应

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

**在请求体中包含音频或视频文件，API 将返回转录的文本结果。**

## 🦺 性能测试

- 测试环境与硬件配置
  - CPU: 13th Gen Intel(R) Core(TM) i9-13950HX 24核 32线程 @ 2.20 GHz
  - GPU: NVIDIA GeForce RTX 4060 Laptop GPU
  - 内存: 64GB
  - 系统: Windows 11

> 单列模式测试

- 我们使用 `faster whisper` 模型作为引擎，然后使用 `CUDA` 进行加速。
- 使用`large-v3`作为推理模型。
- 异步模型池的最大并发数`MAX_CONCURRENT_TASKS`设置为 1。
- 使用一个时长39秒的短视频作为测试文件，连续发送5个请求，所有任务全部完成的总耗时为 32 秒。

> 并发模式测试

- 待添加。

## 📝 代办清单

- 完善爬虫模块，计划添加并支持更多平台。
- 完善任务流系统，实现一个由事件或时间驱动的自动化工作流系统。
- 添加LLM的支持，转录完成的文本可以直接用于进一步处理，如内容摘要、语义分析等，适合二次分析或文本挖掘需求。
- 优化数据库结构和数据库设计，计划对Redis进行支持，并且计划添加更多字段，数据库以后可以存放更多数据。
- 添加部署脚本，编写一个一键部署脚本方便用户使用bash快速部署本项目。
- 使用Docker容器化项目，计划添加对容器的支持，以及自动化的容器编译脚本。

## 🔧 默认配置文件

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

## 🛡️ 许可协议

本项目基于 [Apache2.0](LICENSE) 开源。

商用以及定制合作，请联系 **Email：evil0ctal1985@gmail.com**

## 📬 联系方式

有任何问题或建议，欢迎通过 [issue](https://github.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API/issues) 与我们联系。

## 🧑‍💻 贡献指南

非常欢迎大家提出意见和建议！可以通过 GitHub issue 与我们联系，如果希望贡献代码，请 fork 项目并提交 pull request。我们期待你的加入！💪
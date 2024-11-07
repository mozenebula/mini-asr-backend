# Whisper-Speech-to-Text-API 🎙️➡️📜

## 本项目还在积极开发和优化中，当前自述文档已过时，请等待下一个版本的更新。

[Chinese](README.md) | [English](README-ZH)

欢迎来到 **[Whisper-Speech-to-Text-API](https://github.com/Evil0ctal/Whisper-Speech-to-Text-API)** 项目！本项目为开发者们提供了一个快速、可靠的 API，通过调用 [OpenAI Whisper](https://github.com/openai/whisper) 模型，将多种格式的视频或音频文件高效转换为文本，适合语音识别、字幕生成和文本分析需求。

## 项目地址 📂

* **GitHub 地址**： [Whisper-Speech-to-Text-API](https://github.com/Evil0ctal/Whisper-Speech-to-Text-API)

## 🌟 特性

* **高性能 API 接口**：基于 FastAPI 实现异步操作，支持后台处理任务并将其存储在 SQLite 数据库中，实现任务可控管理。
* **多格式支持**：支持音频文件、视频文件 (如 MP4) 等多种格式，转换基于 `ffmpeg`，确保高兼容性。
* **CUDA 加速**：为有 GPU 的用户提供 CUDA 加速处理，显著提高转录速度。
* **模型优化**：精细调优后的 Whisper 模型，更高的识别精度，适用于多语言音频识别。（敬请期待🔜）
* **文本分析**：支持文本内容的进一步处理，如摘要生成、内容分析等，满足二次开发需求。
* **自动检测语言**: Whisper模型支持自动语言检测，将使用媒体文件的前30秒来自动设置目标语言。


## 🚀 快速部署

1. **Python 环境**：确保 Python 版本 >= 3.8，推荐使用 3.12版本，本项目广泛使用 `asyncio` 库进行异步处理。
2. **安装 FFmpeg**：根据你的系统来执行以下命令来安装 FFmpeg。
   ```
   # Ubuntu or Debian System
   sudo apt update && sudo apt install ffmpeg
   ​
   # Arch Linux System
   sudo pacman -S ffmpeg
   ​
   # MacOS System -> Homebrew
   brew install ffmpeg
   ​
   # Windows System -> Chocolatey(Method one)
   choco install ffmpeg
   ​
   # Windows System -> Scoop(Method two)
   scoop install ffmpeg
   ```
3. **安装 CUDA**：如需 GPU 加速，请下载并安装 [CUDA](https://developer.nvidia.com/cuda-12-4-0-download-archive)，仅使用 CPU 的用户可跳过。
4. **安装支持CUDA的PyTorch**: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
5. **安装项目依赖**: `pip install -r requirements.txt`

## ⚗️ 技术栈

* **[Whisper](https://github.com/openai/whisper)** - 语音识别模型
* **[ffmpeg](https://ffmpeg.org/)** - 音视频格式转换
* **[torch](https://pytorch.org/)** - 深度学习框架
* **[FastAPI](https://github.com/fastapi/fastapi)** - 高性能 API 框架
* **[aiofile](https://github.com/Tinche/aiofiles)** - 异步文件操作
* **[aiosqlite](https://github.com/omnilib/aiosqlite)** - 异步数据库操作
* **[moviepy](https://github.com/Zulko/moviepy)** - 视频编辑
* **[pydub](https://github.com/jiaaro/pydub)** - 音频编辑

## 💡 项目结构

```
./📂 Whisper-Speech-to-Text-API/
├── 📂 app/                        # 主应用目录
│   ├── 📂 api/                    # API 路由
│   │   ├── 📄 health_check.py     # 健康检查接口
│   │   └── 📄 transcribe.py       # 转录功能接口
│   ├── 📂 database/               # 数据库模块
│   │   ├── 📄 database.py         # 数据库连接与初始化
│   │   └── 📄 models.py           # 数据库模型定义
│   ├── 📂 models/                 # 数据模型
│   │   └── 📄 APIResponseModel.py # API 响应模型
│   ├── 📂 services/               # 服务层逻辑
│   │   ├── 📄 whisper_service.py  # Whisper 模型处理逻辑
│   │   └── 📄 whisper_service_instance.py # Whisper 服务单例
│   ├── 📂 utils/                  # 实用工具
│   │   ├── 📄 file_utils.py       # 文件处理工具
│   │   └── 📄 logging_utils.py    # 日志处理工具
│   └── 📄 main.py                 # 应用启动入口
├── 📂 config/                     # 配置文件
│   └── 📄 settings.py             # 应用设置
├── 📂 scripts/                    # 脚本文件
│   ├── 📄 run_server.sh           # 服务器启动脚本
│   └── 📄 setup.sh                # 环境初始化脚本
├── 📁 log_files/                  # 📒 默认日志文件夹
├── 📁 temp_files/                 # 📂 默认临时文件夹
├── 📄 requirements.txt            # 依赖库列表
├── 📄 start.py                    # 启动脚本
└── 📄 tasks.db                    # 📊 默认数据库文件
```

## 🛠️ 使用指南

- 切换到项目目录，使用下面的命令启动API服务：
- `python3 start.py`
- 随后你可以访问`http://localhost`来查看接口文档，并且在网页上测试。

### API 使用示例

- 添加一个识别任务

```curl
PLACEHOLDER
```

- 响应

```json
PLACEHOLDER
```

**在请求体中包含音频或视频文件，API 将返回转录的文本结果。**

### 性能测试

- 测试环境与硬件配置
  - CPU: 13th Gen Intel(R) Core(TM) i9-13950HX 24核 32线程 @ 2.20 GHz
  - GPU: NVIDIA GeForce RTX 4060 Laptop GPU
  - 内存: 64GB
  - 系统: Windows 11

> 单列模式测试

- 我们使用 `faster whisper` 模型作为引擎，然后使用 `CUDA` 进行加速。
- 使用`large-v3`作为推理模型。
- 异步模型池的最大并发数`MAX_CONCURRENT_TASKS`设置为 1。
- 启动项目耗时：
    ```text
    2024-10-29 23:55:33,994 - app.database.database - INFO - Database engine and session factory initialized.
    2024-10-29 23:55:34,015 - app.database.database - INFO - Database tables created successfully.
    2024-10-29 23:55:34,047 - app.model_pool.async_model_pool - INFO - Initializing AsyncModelPool with 1 instances...
    2024-10-29 23:55:34,048 - app.model_pool.async_model_pool - INFO - 
                Attempting to create a new model instance:
                Engine           : faster_whisper
                Model name       : large-v3
                Device           : auto
                Current pool size: 0
                
    2024-10-29 23:55:37,243 - app.model_pool.async_model_pool - INFO - 
                Successfully created and added a new model instance to the pool.
                Engine           : faster_whisper
                Model name       : large-v3
                Device           : auto
                Current pool size: 1
                
    2024-10-29 23:55:37,243 - app.model_pool.async_model_pool - INFO - Successfully initialized AsyncModelPool with 1 instances.
    2024-10-29 23:55:37,244 - app.utils.file_utils - DEBUG - Temporary directory set to C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files
    2024-10-29 23:55:37,246 - app.services.task_processor - INFO - TaskProcessor started.
    2024-10-29 23:55:37,251 - app.services.task_processor - INFO - No tasks to process, waiting for new tasks...
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://0.0.0.0:80 (Press CTRL+C to quit)
    ```
- 使用一个时长39秒的短视频作为测试文件，连续发送5个请求，每个请求将创建一个后台任务。
- 任务日志，总耗时为 32 秒，且主线程无阻塞。
    ```text
    2024-10-30 00:02:04,216 - app.utils.file_utils - DEBUG - Generated unique file name: 2b9278d72bed4af8b4a735494cfeeffe.mp4
  2024-10-30 00:02:04,216 - app.utils.file_utils - DEBUG - Name uploaded file to: 2b9278d72bed4af8b4a735494cfeeffe.mp4
  2024-10-30 00:02:04,223 - app.utils.file_utils - DEBUG - Uploaded file saved successfully.
  2024-10-30 00:02:04,223 - app.services.whisper_service - DEBUG - Audio file saved to temporary path: C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files\2b9278d72bed4af8b4a735494cfeeffe.mp4
  2024-10-30 00:02:04,224 - app.services.whisper_service - DEBUG - Getting duration of audio file: C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files\2b9278d72bed4af8b4a735494cfeeffe.mp4
  2024-10-30 00:02:04,410 - app.services.whisper_service - DEBUG - Audio file duration: 39.61 seconds
  2024-10-30 00:02:04,431 - app.services.whisper_service - INFO - Created transcription task with ID: 1
  INFO:     127.0.0.1:57648 - "POST /api/transcribe/task/create HTTP/1.1" 200 OK
  2024-10-30 00:02:04,980 - app.utils.file_utils - DEBUG - Generated unique file name: a30adc4c40ed49a8ac620fc64e86eb6f.mp4
  2024-10-30 00:02:04,980 - app.utils.file_utils - DEBUG - Name uploaded file to: a30adc4c40ed49a8ac620fc64e86eb6f.mp4
  2024-10-30 00:02:04,987 - app.utils.file_utils - DEBUG - Uploaded file saved successfully.
  2024-10-30 00:02:04,988 - app.services.whisper_service - DEBUG - Audio file saved to temporary path: C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files\a30adc4c40ed49a8ac620fc64e86eb6f.mp4
  2024-10-30 00:02:04,988 - app.services.whisper_service - DEBUG - Getting duration of audio file: C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files\a30adc4c40ed49a8ac620fc64e86eb6f.mp4
  2024-10-30 00:02:05,194 - app.services.whisper_service - DEBUG - Audio file duration: 39.61 seconds
  2024-10-30 00:02:05,217 - app.services.whisper_service - INFO - Created transcription task with ID: 2
  INFO:     127.0.0.1:57648 - "POST /api/transcribe/task/create HTTP/1.1" 200 OK
  2024-10-30 00:02:05,730 - app.utils.file_utils - DEBUG - Generated unique file name: 34756286f2854d88bda330fc902cd088.mp4
  2024-10-30 00:02:05,730 - app.utils.file_utils - DEBUG - Name uploaded file to: 34756286f2854d88bda330fc902cd088.mp4
  2024-10-30 00:02:05,736 - app.utils.file_utils - DEBUG - Uploaded file saved successfully.
  2024-10-30 00:02:05,737 - app.services.whisper_service - DEBUG - Audio file saved to temporary path: C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files\34756286f2854d88bda330fc902cd088.mp4
  2024-10-30 00:02:05,737 - app.services.whisper_service - DEBUG - Getting duration of audio file: C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files\34756286f2854d88bda330fc902cd088.mp4
  2024-10-30 00:02:05,960 - app.services.whisper_service - DEBUG - Audio file duration: 39.61 seconds
  2024-10-30 00:02:05,981 - app.services.whisper_service - INFO - Created transcription task with ID: 3
  INFO:     127.0.0.1:57648 - "POST /api/transcribe/task/create HTTP/1.1" 200 OK
  2024-10-30 00:02:06,382 - app.utils.file_utils - DEBUG - Generated unique file name: 200de82c66d34ea186434328a4d5564f.mp4
  2024-10-30 00:02:06,382 - app.utils.file_utils - DEBUG - Name uploaded file to: 200de82c66d34ea186434328a4d5564f.mp4
  2024-10-30 00:02:06,392 - app.utils.file_utils - DEBUG - Uploaded file saved successfully.
  2024-10-30 00:02:06,392 - app.services.whisper_service - DEBUG - Audio file saved to temporary path: C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files\200de82c66d34ea186434328a4d5564f.mp4
  2024-10-30 00:02:06,392 - app.services.whisper_service - DEBUG - Getting duration of audio file: C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files\200de82c66d34ea186434328a4d5564f.mp4
  2024-10-30 00:02:06,627 - app.services.whisper_service - DEBUG - Audio file duration: 39.61 seconds
  2024-10-30 00:02:06,653 - app.services.whisper_service - INFO - Created transcription task with ID: 4
  INFO:     127.0.0.1:57648 - "POST /api/transcribe/task/create HTTP/1.1" 200 OK
  2024-10-30 00:02:07,090 - app.utils.file_utils - DEBUG - Generated unique file name: d3785a40417447b295ee187ced6364dd.mp4
  2024-10-30 00:02:07,090 - app.utils.file_utils - DEBUG - Name uploaded file to: d3785a40417447b295ee187ced6364dd.mp4
  2024-10-30 00:02:07,100 - app.utils.file_utils - DEBUG - Uploaded file saved successfully.
  2024-10-30 00:02:07,100 - app.services.whisper_service - DEBUG - Audio file saved to temporary path: C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files\d3785a40417447b295ee187ced6364dd.mp4
  2024-10-30 00:02:07,100 - app.services.whisper_service - DEBUG - Getting duration of audio file: C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files\d3785a40417447b295ee187ced6364dd.mp4
  2024-10-30 00:02:07,215 - app.services.task_processor - INFO - 
                  Processing queued task:
                  ID          : 1
                  Engine      : faster_whisper
                  Priority    : TaskPriority.NORMAL
                  File        : Example.mp4
                  Size        : 5273783 bytes
                  Duration    : 39.61 seconds
                  Created At  : 2024-10-30 07:02:04.412974
                  Output URL  : http://127.0.0.1/api/transcribe/tasks/result?task_id=1
                  
  2024-10-30 00:02:07,216 - app.model_pool.async_model_pool - INFO - Attempting to retrieve a model instance from the pool...
  2024-10-30 00:02:07,216 - app.model_pool.async_model_pool - INFO - 
              Model instance successfully retrieved from the pool.
              Current pool size: 1 / Max size: 1
              
  2024-10-30 00:02:07,342 - app.services.whisper_service - DEBUG - Audio file duration: 39.61 seconds
  2024-10-30 00:02:07,618 - app.services.whisper_service - INFO - Created transcription task with ID: 5
  INFO:     127.0.0.1:57648 - "POST /api/transcribe/task/create HTTP/1.1" 200 OK
  2024-10-30 00:02:14,482 - app.services.task_processor - INFO - 
                      Task processed successfully:
                      ID          : 1
                      Engine      : faster_whisper
                      Priority    : TaskPriority.NORMAL
                      File        : Example.mp4
                      Size        : 5273783 bytes
                      Duration    : 39.61 seconds
                      Created At  : 2024-10-30 07:02:04.412974
                      Output URL  : http://127.0.0.1/api/transcribe/tasks/result?task_id=1
                      Language    : zh
                      
  2024-10-30 00:02:14,494 - app.model_pool.async_model_pool - INFO - 
              Model instance successfully returned to the pool.
              Current pool size (after return): 1
              
  2024-10-30 00:02:14,496 - app.utils.file_utils - DEBUG - File deleted successfully: C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files\2b9278d72bed4af8b4a735494cfeeffe.mp4
  2024-10-30 00:02:14,497 - app.services.task_processor - INFO - Task 1 processed successfully.
  2024-10-30 00:02:14,500 - app.services.task_processor - INFO - 
                  Processing queued task:
                  ID          : 2
                  Engine      : faster_whisper
                  Priority    : TaskPriority.NORMAL
                  File        : Example.mp4
                  Size        : 5273783 bytes
                  Duration    : 39.61 seconds
                  Created At  : 2024-10-30 07:02:05.196961
                  Output URL  : http://127.0.0.1/api/transcribe/tasks/result?task_id=2
                  
  2024-10-30 00:02:14,500 - app.model_pool.async_model_pool - INFO - Attempting to retrieve a model instance from the pool...
  2024-10-30 00:02:14,500 - app.model_pool.async_model_pool - INFO - 
              Model instance successfully retrieved from the pool.
              Current pool size: 1 / Max size: 1
              
  2024-10-30 00:02:20,043 - app.services.task_processor - INFO - 
                      Task processed successfully:
                      ID          : 2
                      Engine      : faster_whisper
                      Priority    : TaskPriority.NORMAL
                      File        : Example.mp4
                      Size        : 5273783 bytes
                      Duration    : 39.61 seconds
                      Created At  : 2024-10-30 07:02:05.196961
                      Output URL  : http://127.0.0.1/api/transcribe/tasks/result?task_id=2
                      Language    : zh
                      
  2024-10-30 00:02:20,056 - app.model_pool.async_model_pool - INFO - 
              Model instance successfully returned to the pool.
              Current pool size (after return): 1
              
  2024-10-30 00:02:20,058 - app.utils.file_utils - DEBUG - File deleted successfully: C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files\a30adc4c40ed49a8ac620fc64e86eb6f.mp4
  2024-10-30 00:02:20,059 - app.services.task_processor - INFO - Task 2 processed successfully.
  2024-10-30 00:02:20,061 - app.services.task_processor - INFO - 
                  Processing queued task:
                  ID          : 3
                  Engine      : faster_whisper
                  Priority    : TaskPriority.NORMAL
                  File        : Example.mp4
                  Size        : 5273783 bytes
                  Duration    : 39.61 seconds
                  Created At  : 2024-10-30 07:02:05.962820
                  Output URL  : http://127.0.0.1/api/transcribe/tasks/result?task_id=3
                  
  2024-10-30 00:02:20,062 - app.model_pool.async_model_pool - INFO - Attempting to retrieve a model instance from the pool...
  2024-10-30 00:02:20,062 - app.model_pool.async_model_pool - INFO - 
              Model instance successfully retrieved from the pool.
              Current pool size: 1 / Max size: 1
              
  2024-10-30 00:02:25,533 - app.services.task_processor - INFO - 
                      Task processed successfully:
                      ID          : 3
                      Engine      : faster_whisper
                      Priority    : TaskPriority.NORMAL
                      File        : Example.mp4
                      Size        : 5273783 bytes
                      Duration    : 39.61 seconds
                      Created At  : 2024-10-30 07:02:05.962820
                      Output URL  : http://127.0.0.1/api/transcribe/tasks/result?task_id=3
                      Language    : zh
                      
  2024-10-30 00:02:25,546 - app.model_pool.async_model_pool - INFO - 
              Model instance successfully returned to the pool.
              Current pool size (after return): 1
              
  2024-10-30 00:02:25,548 - app.utils.file_utils - DEBUG - File deleted successfully: C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files\34756286f2854d88bda330fc902cd088.mp4
  2024-10-30 00:02:25,549 - app.services.task_processor - INFO - Task 3 processed successfully.
  2024-10-30 00:02:25,551 - app.services.task_processor - INFO - 
                  Processing queued task:
                  ID          : 4
                  Engine      : faster_whisper
                  Priority    : TaskPriority.NORMAL
                  File        : Example.mp4
                  Size        : 5273783 bytes
                  Duration    : 39.61 seconds
                  Created At  : 2024-10-30 07:02:06.629327
                  Output URL  : http://127.0.0.1/api/transcribe/tasks/result?task_id=4
                  
  2024-10-30 00:02:25,552 - app.model_pool.async_model_pool - INFO - Attempting to retrieve a model instance from the pool...
  2024-10-30 00:02:25,552 - app.model_pool.async_model_pool - INFO - 
              Model instance successfully retrieved from the pool.
              Current pool size: 1 / Max size: 1
              
  2024-10-30 00:02:30,910 - app.services.task_processor - INFO - 
                      Task processed successfully:
                      ID          : 4
                      Engine      : faster_whisper
                      Priority    : TaskPriority.NORMAL
                      File        : Example.mp4
                      Size        : 5273783 bytes
                      Duration    : 39.61 seconds
                      Created At  : 2024-10-30 07:02:06.629327
                      Output URL  : http://127.0.0.1/api/transcribe/tasks/result?task_id=4
                      Language    : zh
                      
  2024-10-30 00:02:30,922 - app.model_pool.async_model_pool - INFO - 
              Model instance successfully returned to the pool.
              Current pool size (after return): 1
              
  2024-10-30 00:02:30,924 - app.utils.file_utils - DEBUG - File deleted successfully: C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files\200de82c66d34ea186434328a4d5564f.mp4
  2024-10-30 00:02:30,925 - app.services.task_processor - INFO - Task 4 processed successfully.
  2024-10-30 00:02:30,927 - app.services.task_processor - INFO - 
                  Processing queued task:
                  ID          : 5
                  Engine      : faster_whisper
                  Priority    : TaskPriority.NORMAL
                  File        : Example.mp4
                  Size        : 5273783 bytes
                  Duration    : 39.61 seconds
                  Created At  : 2024-10-30 07:02:07.344753
                  Output URL  : http://127.0.0.1/api/transcribe/tasks/result?task_id=5
                  
  2024-10-30 00:02:30,928 - app.model_pool.async_model_pool - INFO - Attempting to retrieve a model instance from the pool...
  2024-10-30 00:02:30,928 - app.model_pool.async_model_pool - INFO - 
              Model instance successfully retrieved from the pool.
              Current pool size: 1 / Max size: 1
              
  2024-10-30 00:02:36,374 - app.services.task_processor - INFO - 
                      Task processed successfully:
                      ID          : 5
                      Engine      : faster_whisper
                      Priority    : TaskPriority.NORMAL
                      File        : Example.mp4
                      Size        : 5273783 bytes
                      Duration    : 39.61 seconds
                      Created At  : 2024-10-30 07:02:07.344753
                      Output URL  : http://127.0.0.1/api/transcribe/tasks/result?task_id=5
                      Language    : zh
                      
  2024-10-30 00:02:36,390 - app.model_pool.async_model_pool - INFO - 
              Model instance successfully returned to the pool.
              Current pool size (after return): 1
              
  2024-10-30 00:02:36,392 - app.utils.file_utils - DEBUG - File deleted successfully: C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files\d3785a40417447b295ee187ced6364dd.mp4
  2024-10-30 00:02:36,393 - app.services.task_processor - INFO - Task 5 processed successfully.
  2024-10-30 00:02:36,396 - app.services.task_processor - INFO - No tasks to process, waiting for new tasks...
    ```

> 并发模式测试

- 我们使用 `faster whisper` 模型作为引擎，然后使用 `CUDA` 进行加速。
- 使用`large-v3`作为推理模型。
- 异步模型池的最大并发数`MAX_CONCURRENT_TASKS`设置为 3。
  - 启动项目耗时：
      ```text
      2024-10-30 00:06:14,792 - app.database.database - INFO - Database engine and session factory initialized.
      2024-10-30 00:06:14,811 - app.database.database - INFO - Database tables created successfully.
      2024-10-30 00:06:14,832 - app.model_pool.async_model_pool - INFO - Initializing AsyncModelPool with 3 instances...
      2024-10-30 00:06:14,832 - app.model_pool.async_model_pool - INFO - 
              Attempting to create a new model instance:
              Engine           : faster_whisper
              Model name       : large-v3
              Device           : auto
              Current pool size: 0
            
      2024-10-30 00:06:14,833 - app.model_pool.async_model_pool - INFO - 
              Attempting to create a new model instance:
              Engine           : faster_whisper
              Model name       : large-v3
              Device           : auto
              Current pool size: 0
            
      2024-10-30 00:06:14,834 - app.model_pool.async_model_pool - INFO - 
              Attempting to create a new model instance:
              Engine           : faster_whisper
              Model name       : large-v3
              Device           : auto
              Current pool size: 0
            
      2024-10-30 00:06:20,943 - app.model_pool.async_model_pool - INFO - 
              Successfully created and added a new model instance to the pool.
              Engine           : faster_whisper
              Model name       : large-v3
              Device           : auto
              Current pool size: 1
            
      2024-10-30 00:06:21,402 - app.model_pool.async_model_pool - INFO - 
              Successfully created and added a new model instance to the pool.
              Engine           : faster_whisper
              Model name       : large-v3
              Device           : auto
              Current pool size: 2
            
      2024-10-30 00:06:21,702 - app.model_pool.async_model_pool - INFO - 
              Successfully created and added a new model instance to the pool.
              Engine           : faster_whisper
              Model name       : large-v3
              Device           : auto
              Current pool size: 3
            
      2024-10-30 00:06:21,702 - app.model_pool.async_model_pool - INFO - Successfully initialized AsyncModelPool with 3 instances.
      2024-10-30 00:06:21,703 - app.utils.file_utils - DEBUG - Temporary directory set to C:\Users\Evil0ctal\PycharmProjects\Whisper-Speech-to-Text-API\temp_files
      2024-10-30 00:06:21,705 - app.services.task_processor - INFO - TaskProcessor started.
      2024-10-30 00:06:21,710 - app.services.task_processor - INFO - No tasks to process, waiting for new tasks...
      INFO:     Application startup complete.
      INFO:     Uvicorn running on http://0.0.0.0:80 (Press CTRL+C to quit)
      ````
- 使用一个时长39秒的短视频作为测试文件，连续发送5个请求，每个请求将创建一个后台任务。
- 任务日志，总耗时为 32 秒，且主线程无阻塞。
    ```text
    2024
    ```

### 文本分析与扩展功能

**转录完成的文本可以直接用于进一步处理，如内容摘要、语义分析等，适合二次分析或文本挖掘需求。**

## 贡献指南

**非常欢迎大家提出意见和建议！可以通过 GitHub issue 与我们联系，如果希望贡献代码，请 fork 项目并提交 pull request。我们期待你的加入！💪**

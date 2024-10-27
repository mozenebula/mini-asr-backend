# Whisper-Speech-to-Text-API 🎙️➡️📜

[Chinese](README.md) | [English](README-EN.md)

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

1. **Python 环境**：确保 Python 版本 >= 3.8，本项目广泛使用 `asyncio` 库进行异步处理。
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
4. **安装支持CUDA的PyTorch**: `python3 -m pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
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
​curl -X 'POST' \
  'http://127.0.0.1/transcribe/task/create' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'verbose=false' \
  -F 'priority=normal' \
  -F 'logprob_threshold=-1' \
  -F 'prepend_punctuations="'\''“¿([{-' \
  -F 'no_speech_threshold=0.6' \
  -F 'clip_timestamps=0' \
  -F 'word_timestamps=false' \
  -F 'temperature=0.2' \
  -F 'hallucination_silence_threshold=0' \
  -F 'condition_on_previous_text=true' \
  -F 'file=@Example.mp4;type=video/mp4' \
  -F 'compression_ratio_threshold=2.4' \
  -F 'append_punctuations="'\''.。,，!！?？:：”)]}、' \
  -F 'initial_prompt='
```

- 响应

```json
{
  "code": 200,
  "router": "http://127.0.0.1/transcribe/task/create",
  "params": {},
  "data": {
    "id": 1,
    "created_at": "2024-10-27T06:40:55.413738",
    "updated_at": null,
    "status": "queued",
    "file_path": "C:\\Users\\Evil0ctal\\PycharmProjects\\Whisper-Speech-to-Text-API\\temp_files\\02fe0aa4265e43ed91532107b9f6303b.mp4",
    "file_name": "Example.mp4",
    "file_size_bytes": 5273783,
    "duration": 39.612,
    "decode_options": {
      "temperature": [
        0.2
      ],
      "verbose": false,
      "compression_ratio_threshold": 2.4,
      "logprob_threshold": -1,
      "no_speech_threshold": 0.6,
      "condition_on_previous_text": true,
      "initial_prompt": "",
      "word_timestamps": false,
      "prepend_punctuations": "\"'“¿([{-",
      "append_punctuations": "\"'.。,，!！?？:：”)]}、",
      "clip_timestamps": [
        0
      ],
      "hallucination_silence_threshold": 0
    },
    "result": null,
    "error_message": null,
    "attempts": 0,
    "priority": "normal",
    "output_url": null,
    "language": null,
    "progress": 0
  }
}
```

- 查看任务结果

```curl
curl -X 'GET' \
  'http://127.0.0.1/transcribe/tasks/result?task_id=1' \
  -H 'accept: application/json'
```

- 响应

```json
{
  "id": 1,
  "created_at": "2024-10-27T06:40:55.413738",
  "updated_at": "2024-10-27T06:45:38.557478",
  "status": "completed",
  "file_path": "C:\\Users\\Evil0ctal\\PycharmProjects\\Whisper-Speech-to-Text-API\\temp_files\\02fe0aa4265e43ed91532107b9f6303b.mp4",
  "file_name": "Example.mp4",
  "file_size_bytes": 5273783,
  "duration": 39.612,
  "decode_options": {
    "temperature": [
      0.2
    ],
    "verbose": false,
    "compression_ratio_threshold": 2.4,
    "logprob_threshold": -1,
    "no_speech_threshold": 0.6,
    "condition_on_previous_text": true,
    "initial_prompt": "",
    "word_timestamps": false,
    "prepend_punctuations": "\"'“¿([{-",
    "append_punctuations": "\"'.。,，!！?？:：”)]}、",
    "clip_timestamps": [
      0
    ],
    "hallucination_silence_threshold": 0
  },
  "result": {
    "text": "我们并没有在一起只是聊了很久的天我知道我们并没有感情每天我们就是问问在干嘛我们就是早安晚安拿大游戏发发呆没话讲就发表情报号下去因为相较于情感的挥霍爱的执照总是要显得繁琐些要好像从来都不好气我是怎么样的人我半夜不睡觉的时候在干嘛摩卡就牵是什么意思我的社交圈我的朋友我的爱好你好像通通不在乎我只是你刚好寂寞的时候我撞了上去刚好我心里还挺知道我们有点两万个的话题当然我稍微能入你的眼刚好而已我们都在场口是心非却又希望对方有所察觉但很多时候沉默都比解释热和悲伤来得更容易",
    "segments": [
      {
        "id": 0,
        "seek": 0,
        "start": 0,
        "end": 1.28,
        "text": "我们并没有在一起",
        "tokens": [
          50365,
          15003,
          3509,
          114,
          17944,
          3581,
          29567,
          50429
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 1,
        "seek": 0,
        "start": 1.28,
        "end": 2.64,
        "text": "只是聊了很久的天",
        "tokens": [
          50429,
          36859,
          40096,
          2289,
          4563,
          25320,
          1546,
          6135,
          50497
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 2,
        "seek": 0,
        "start": 2.64,
        "end": 4.2,
        "text": "我知道我们并没有感情",
        "tokens": [
          50497,
          33838,
          15003,
          3509,
          114,
          17944,
          9709,
          10570,
          50575
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 3,
        "seek": 0,
        "start": 4.2,
        "end": 5.84,
        "text": "每天我们就是问问在干嘛",
        "tokens": [
          50575,
          23664,
          6135,
          15003,
          5620,
          22064,
          22064,
          3581,
          26111,
          20722,
          50657
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 4,
        "seek": 0,
        "start": 5.84,
        "end": 7.2,
        "text": "我们就是早安晚安",
        "tokens": [
          50657,
          15003,
          5620,
          21176,
          16206,
          27080,
          16206,
          50725
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 5,
        "seek": 0,
        "start": 7.2,
        "end": 8.52,
        "text": "拿大游戏发发呆",
        "tokens": [
          50725,
          24351,
          3582,
          9592,
          116,
          1486,
          237,
          28926,
          28926,
          3606,
          228,
          50791
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 6,
        "seek": 0,
        "start": 8.52,
        "end": 10.56,
        "text": "没话讲就发表情报号下去",
        "tokens": [
          50791,
          10062,
          21596,
          39255,
          3111,
          28926,
          17571,
          10570,
          49817,
          26987,
          34473,
          50893
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 7,
        "seek": 0,
        "start": 10.56,
        "end": 12.44,
        "text": "因为相较于情感的挥霍",
        "tokens": [
          50893,
          34627,
          15106,
          9830,
          225,
          37732,
          10570,
          9709,
          1546,
          8501,
          98,
          18594,
          235,
          50987
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 8,
        "seek": 0,
        "start": 12.44,
        "end": 14.76,
        "text": "爱的执照总是要显得繁琐些",
        "tokens": [
          50987,
          27324,
          1546,
          3416,
          100,
          32150,
          33440,
          1541,
          4275,
          1431,
          122,
          5916,
          23141,
          223,
          10568,
          238,
          13824,
          51103
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 9,
        "seek": 0,
        "start": 14.76,
        "end": 15.92,
        "text": "要好像从来都不好气",
        "tokens": [
          51103,
          4275,
          33242,
          35630,
          6912,
          7182,
          15769,
          42204,
          51161
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 10,
        "seek": 0,
        "start": 15.92,
        "end": 16.96,
        "text": "我是怎么样的人",
        "tokens": [
          51161,
          15914,
          48200,
          29979,
          51213
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 11,
        "seek": 0,
        "start": 16.96,
        "end": 18.96,
        "text": "我半夜不睡觉的时候在干嘛",
        "tokens": [
          51213,
          1654,
          30018,
          30124,
          1960,
          40490,
          24447,
          49873,
          3581,
          26111,
          20722,
          51313
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 12,
        "seek": 0,
        "start": 18.96,
        "end": 20.400000000000002,
        "text": "摩卡就牵是什么意思",
        "tokens": [
          51313,
          34783,
          102,
          32681,
          3111,
          6935,
          113,
          1541,
          10440,
          16697,
          51385
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 13,
        "seek": 0,
        "start": 20.400000000000002,
        "end": 21.44,
        "text": "我的社交圈",
        "tokens": [
          51385,
          14200,
          27658,
          28455,
          2523,
          230,
          51437
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 14,
        "seek": 0,
        "start": 21.44,
        "end": 22.32,
        "text": "我的朋友",
        "tokens": [
          51437,
          14200,
          19828,
          51481
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 15,
        "seek": 0,
        "start": 22.32,
        "end": 23,
        "text": "我的爱好",
        "tokens": [
          51481,
          14200,
          27324,
          2131,
          51515
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 16,
        "seek": 0,
        "start": 23,
        "end": 24.52,
        "text": "你好像通通不在乎我",
        "tokens": [
          51515,
          26410,
          12760,
          19550,
          19550,
          1960,
          3581,
          2930,
          236,
          1654,
          51591
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 17,
        "seek": 0,
        "start": 24.52,
        "end": 25.84,
        "text": "只是你刚好寂寞的时候",
        "tokens": [
          51591,
          36859,
          2166,
          49160,
          2131,
          4510,
          224,
          4510,
          252,
          49873,
          51657
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 18,
        "seek": 0,
        "start": 25.84,
        "end": 26.96,
        "text": "我撞了上去",
        "tokens": [
          51657,
          1654,
          20559,
          252,
          2289,
          5708,
          6734,
          51713
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 19,
        "seek": 0,
        "start": 26.96,
        "end": 28.240000000000002,
        "text": "刚好我心里还挺",
        "tokens": [
          51713,
          49160,
          2131,
          1654,
          7945,
          15759,
          14852,
          41046,
          51777
        ],
        "temperature": 0.2,
        "avg_logprob": -0.21540247599283854,
        "compression_ratio": 1.4733727810650887,
        "no_speech_prob": 3.287499161785945e-10
      },
      {
        "id": 20,
        "seek": 2824,
        "start": 28.24,
        "end": 30.36,
        "text": "知道我们有点两万个的话题",
        "tokens": [
          50365,
          7758,
          15003,
          2412,
          12579,
          36257,
          23570,
          7549,
          44575,
          30716,
          50471
        ],
        "temperature": 0.2,
        "avg_logprob": -0.2133265408602628,
        "compression_ratio": 1.1271676300578035,
        "no_speech_prob": 0.005595638416707516
      },
      {
        "id": 21,
        "seek": 2824,
        "start": 30.36,
        "end": 31.919999999999998,
        "text": "当然我稍微能入你的眼",
        "tokens": [
          50471,
          40486,
          1654,
          10415,
          235,
          39152,
          8225,
          14028,
          18961,
          25281,
          50549
        ],
        "temperature": 0.2,
        "avg_logprob": -0.2133265408602628,
        "compression_ratio": 1.1271676300578035,
        "no_speech_prob": 0.005595638416707516
      },
      {
        "id": 22,
        "seek": 2824,
        "start": 31.919999999999998,
        "end": 32.839999999999996,
        "text": "刚好而已",
        "tokens": [
          50549,
          49160,
          2131,
          48420,
          50595
        ],
        "temperature": 0.2,
        "avg_logprob": -0.2133265408602628,
        "compression_ratio": 1.1271676300578035,
        "no_speech_prob": 0.005595638416707516
      },
      {
        "id": 23,
        "seek": 2824,
        "start": 32.839999999999996,
        "end": 34.44,
        "text": "我们都在场口是心非",
        "tokens": [
          50595,
          15003,
          7182,
          3581,
          50255,
          18144,
          1541,
          7945,
          12107,
          50675
        ],
        "temperature": 0.2,
        "avg_logprob": -0.2133265408602628,
        "compression_ratio": 1.1271676300578035,
        "no_speech_prob": 0.005595638416707516
      },
      {
        "id": 24,
        "seek": 2824,
        "start": 34.44,
        "end": 36.239999999999995,
        "text": "却又希望对方有所察觉",
        "tokens": [
          50675,
          5322,
          112,
          17047,
          29955,
          8713,
          9249,
          2412,
          5966,
          47550,
          24447,
          50765
        ],
        "temperature": 0.2,
        "avg_logprob": -0.2133265408602628,
        "compression_ratio": 1.1271676300578035,
        "no_speech_prob": 0.005595638416707516
      },
      {
        "id": 25,
        "seek": 2824,
        "start": 36.239999999999995,
        "end": 37.08,
        "text": "但很多时候",
        "tokens": [
          50765,
          8395,
          20778,
          29111,
          50807
        ],
        "temperature": 0.2,
        "avg_logprob": -0.2133265408602628,
        "compression_ratio": 1.1271676300578035,
        "no_speech_prob": 0.005595638416707516
      },
      {
        "id": 26,
        "seek": 2824,
        "start": 37.08,
        "end": 39.599999999999994,
        "text": "沉默都比解释热和悲伤来得更容易",
        "tokens": [
          50807,
          3308,
          231,
          6173,
          246,
          7182,
          11706,
          17278,
          5873,
          232,
          23661,
          255,
          12565,
          14696,
          110,
          7384,
          97,
          6912,
          5916,
          19002,
          49212,
          50933
        ],
        "temperature": 0.2,
        "avg_logprob": -0.2133265408602628,
        "compression_ratio": 1.1271676300578035,
        "no_speech_prob": 0.005595638416707516
      }
    ],
    "language": "zh"
  },
  "error_message": null,
  "attempts": 0,
  "priority": "normal",
  "output_url": null,
  "language": null,
  "progress": 0
}
```

**在请求体中包含音频或视频文件，API 将返回转录的文本结果。**

### 文本分析与扩展功能

**转录完成的文本可以直接用于进一步处理，如内容摘要、语义分析等，适合二次分析或文本挖掘需求。**

## 贡献指南

**非常欢迎大家提出意见和建议！可以通过 GitHub issue 与我们联系，如果希望贡献代码，请 fork 项目并提交 pull request。我们期待你的加入！💪**

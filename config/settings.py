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
        description: str = "⚡ A high-performance asynchronous API for Automatic Speech Recognition (ASR) and translation. No need to purchase the Whisper API—perform inference using a locally running Whisper model with support for multi-GPU concurrency and designed for distributed deployment. It also includes built-in crawlers for social media platforms like TikTok and Douyin, enabling seamless media processing from multiple social platforms. This provides a powerful and scalable solution for automated media content data processing."
        # 项目版本 | Project version
        version: str = "1.0.5"
        # Swagger 文档 URL | Swagger docs URL
        docs_url: str = "/"
        # 是否开启 debug 模式 | Whether to enable debug mode
        debug: bool = False
        # 当检测到项目代码变动时是否自动重载项目 | Whether to automatically reload the project when changes to the project code are detected
        reload_on_file_change: bool = os.getenv("RELOAD_ON_FILE_CHANGE", False)
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
        web_cookie: str = os.getenv("DOUYIN_WEB_COOKIE", "ttwid=1%7CtnAW08ODesZvyAEgKUFBHCdUJpqmV_Lwrr9uwavi5AI%7C1740556660%7Cc081872970e7b3431eda3b195dddf6c77a0c9c90e76f0d12ec71a89ea0cfbd72; UIFID_TEMP=4ba2d7b73ad9c101231aefda203ea0f7acfb3ef443b5511c9ed864710f1d25b809b7cbc70826c54ce7cb934f4c3d625d80505b6525f871651907aa420a563ec7d6fbe3ddbdd34f11e41f2ccf730b4fe2; hevc_supported=true; fpk1=U2FsdGVkX1+v1+PUShZoeCk0nEDDnS2O9tlrmtbRDxCFdiA2lPsRxnx538hD4xyTQDtAo0LNW6sAtkxR3PiY3w==; fpk2=b801d494f122793b0612636bfa234b9c; s_v_web_id=verify_m7lmhzwb_5K7C6FiT_YDba_4Ab5_8Juj_XaJOlUdScJb1; xgplayer_user_id=438503653740; passport_csrf_token=e56a9224fbf23a7bbbb03ae0de64c94e; passport_csrf_token_default=e56a9224fbf23a7bbbb03ae0de64c94e; __security_mc_1_s_sdk_crypt_sdk=01e53f13-46c0-b023; bd_ticket_guard_client_web_domain=2; is_staff_user=false; store-region=cn-sh; store-region-src=uid; UIFID=4ba2d7b73ad9c101231aefda203ea0f7acfb3ef443b5511c9ed864710f1d25b827026b34aa788a9b527c21d9d87ae7153eaeac151d723db7488c7437fa125b892b4e294b827794cff540e5e8d15bccc594f3464d6176cf4b961d1e2a2e06737d8dc3f9432c125cc088480e57263d53e556e59864144d344bd9d4dc1cd52edbdddd2f7526904562d5036106f72342e204ed35ad3ad143fbecfdec55af5c1415ed; SelfTabRedDotControl=%5B%5D; _bd_ticket_crypt_doamin=2; __security_mc_1_s_sdk_cert_key=de2deda7-474e-9c72; __security_server_data_status=1; my_rd=2; MONITOR_WEB_ID=3660af6a-2466-46c1-b9ae-68851399b331; SEARCH_RESULT_LIST_TYPE=%22single%22; __ac_nonce=067cff261003ec2d62d1d; __ac_signature=_02B4Z6wo00f01kjNnOgAAIDDYckClceNGZZI7ZhAAPYL54; douyin.com; xg_device_score=7.561096203079858; device_web_cpu_core=8; device_web_memory_size=8; upgrade_tag=1; dy_swidth=1440; dy_sheight=900; strategyABtestKey=%221741681251.572%22; publish_badge_show_info=%220%2C0%2C0%2C1741681255162%22; sso_uid_tt=e5fc42d9ac1ceff420725fe27c537c63; sso_uid_tt_ss=e5fc42d9ac1ceff420725fe27c537c63; toutiao_sso_user=993bd4d9c109c3cbde8a69fa7a645283; toutiao_sso_user_ss=993bd4d9c109c3cbde8a69fa7a645283; sid_ucp_sso_v1=1.0.0-KDU1M2Q3YTViODYwOTg1MTA2YmRhMDhiNzQxY2ViY2Y4NTZlY2RmODcKCRDs5L--BhjvMRoCbGYiIDk5M2JkNGQ5YzEwOWMzY2JkZThhNjlmYTdhNjQ1Mjgz; ssid_ucp_sso_v1=1.0.0-KDU1M2Q3YTViODYwOTg1MTA2YmRhMDhiNzQxY2ViY2Y4NTZlY2RmODcKCRDs5L--BhjvMRoCbGYiIDk5M2JkNGQ5YzEwOWMzY2JkZThhNjlmYTdhNjQ1Mjgz; is_dash_user=1; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1440%2C%5C%22screen_height%5C%22%3A900%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A8%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A150%7D%22; biz_trace_id=52e8a4fa; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e5827292771273f27303d31303337343d3334313234272927676c715a75776a716a666a69273f2763646976602778; bit_env=OpwU9T5cNK4KZWsu-ZpijpvWO7VUKkSPaecTbvlEwabzlm2q5I0aEMqZDvPLCdTgwrOUC1hW18jMHy2erLajrcEp9A3WaPc6APzTeP2_Y7FGxarLqS-aS-oJZtLCh5x7P5x_fSSCsi2Y-nlaIstThd_zKURVOnrwkAMn2YCLKRM6BxHHJwLmuC16rFNAEI9cqXMdbj545gaVV-Z7wHMn0IUBuh4OtOUHJQ8ZUlOK6VrDLS5Nd4FmjZ1UObj0DD0UQuswRcv3X5RYzUgmtzGL2T5o6uu1TiyHFGeYmUmEPLDpvpMbj3YlpF4SV-k3wMDFWJBbcX4ExutdADkykbC9bQgic7ETflHCZ2Fb_WlenrlowJ-tXX--fc2n49iDDaUk7xnxxRP4JyQuBJTWWahm5Wq_jbUFqe13Vo6r2nyqTpt43wYTxc9mO63NGcGlTkd82qZ5svFU-muz1Y3FudihBuAiRLSwIW8AkOY2muFtOwtCwgurWEorNb83GdLtKTC5x9en8_8VpAOcrw7iDXJ_1ybsUr1C2tGpWjQVxxezwjI%3D; gulu_source_res=eyJwX2luIjoiNGZjZWI1ZTVhMjMzZmQ3MTNkNjU2YjQ4NTA2NTdhOTdjN2QxMzZlODc0YTMyMTA1YTExNGVjYjg3ZDA4YjQ4OSJ9; passport_auth_mix_state=5vu0vx4p6eq8qyzadzwohi64c6th29imgwa1i83eagh8carv; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; download_guide=%221%2F20250311%2F0%22; passport_mfa_token=CjeOjz5PKpa5x4MgW6RbOtpmTVYoMis9QfMMRow%2FfL8m5%2F7Qz%2F9uh%2FFx%2FrPY6JRn4XxLU7xWXPrEGkoKPEMNATdMS%2B4iS7kJItPocI48cfJK3%2Frl5rhskNVboyTDExyNQ2ffAWnsSoo4lwI0Guh84%2FeKIFNKpFqO1RDQ3OsNGPax0WwgAiIBA2mdp6U%3D; d_ticket=b568c5ec5094dd777d95142affcbd2bb928d8; passport_assist_user=CkGYUefPwPvIQ4H7WK3beivaR3LALqot_ma5awrAMeoy-AqE9SMZnG4Qzzzp9ETcrcIia822BGuwD3cv8dTKHfSRshpKCjy_pW2qtZk7c9XUc_Fd5fl-MERIOPdlkSkuUHbzraOqdh5tcjrL_KXmNNzM04v2kDSPOv-ajcCYHL7OSFkQ0NzrDRiJr9ZUIAEiAQPzf7uQ; n_mh=KQXyNbWYmCqUn8kdWRsFRJOPgO6bBsSw3BRc5lF0u-Y; passport_auth_status=46b5181288a87c987e6eebb85f9d4639%2Cff52b31baae013983a2a5f742ac719bb; passport_auth_status_ss=46b5181288a87c987e6eebb85f9d4639%2Cff52b31baae013983a2a5f742ac719bb; sid_guard=576736adac9ec6556c3962de94b7ad9e%7C1741681337%7C5184000%7CSat%2C+10-May-2025+08%3A22%3A17+GMT; uid_tt=1ba3e54e6fe6ec34a5890bcc1e28a746; uid_tt_ss=1ba3e54e6fe6ec34a5890bcc1e28a746; sid_tt=576736adac9ec6556c3962de94b7ad9e; sessionid=576736adac9ec6556c3962de94b7ad9e; sessionid_ss=576736adac9ec6556c3962de94b7ad9e; sid_ucp_v1=1.0.0-KGZlYjhmYjc3ZmQzNjFhMzgxZjVkMTMyYmQ0ZjExOGIyZWIxNmZmYWQKIQjduYCEqIyrAhC55b--BhjvMSAMMI6RoJkGOAJA8QdIBBoCaGwiIDU3NjczNmFkYWM5ZWM2NTU2YzM5NjJkZTk0YjdhZDll; ssid_ucp_v1=1.0.0-KGZlYjhmYjc3ZmQzNjFhMzgxZjVkMTMyYmQ0ZjExOGIyZWIxNmZmYWQKIQjduYCEqIyrAhC55b--BhjvMSAMMI6RoJkGOAJA8QdIBBoCaGwiIDU3NjczNmFkYWM5ZWM2NTU2YzM5NjJkZTk0YjdhZDll; login_time=1741681337490; IsDouyinActive=true; home_can_add_dy_2_desktop=%221%22; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAU0TWhO9lgnwmchwJw3SK_y7xg-Yq2JlBv-v06DxooLMeMpP_KOmaBEnNy9vh4H0n%2F1741708800000%2F0%2F1741681339711%2F0%22; _bd_ticket_crypt_cookie=b923d6df437c20ee6a291fc01fca37c1; __security_mc_1_s_sdk_sign_data_key_web_protect=0fd0fee9-48c3-9fa2; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCQmZuMU5QemtlNkMwSVlWRmM3MDNsalF3RElRVWhNbEVoa3ZoczRNSnE1dDcra1BpVkZmYlo5L1NuRVFSQzdkOUJhRkpsaHgrekRyRmgvV2p6akdPTmc9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; WallpaperGuide=%7B%22showTime%22%3A1741681340945%2C%22closeTime%22%3A0%2C%22showCount%22%3A1%2C%22cursor1%22%3A10%2C%22cursor2%22%3A2%7D; odin_tt=341a36d37957a56f4068a9409d85b578a3646c294732fa5153a23d5b1cbdd0071755a952473f47e75d0955f4202ebebefce218abf4064b0f023e93e407baeb6d; passport_fe_beating_status=true; SelectedFeedCache=%22U2FsdGVkX1%2F5afKXgO4efswMJPjcDMugRCzsBtsJtlA8wDZs3DGNDMM19DAO%2B%2F4zuxeEwJcN2hdTEm4CPLi5lBlvJoWJG18EBUDB%2FwMen9rvjtuuxhK7ZW%2B0%2FWVMY%2B3iNLL8tGp809dlJX68OiSLDT8tPqCumLcYJXXt090o86o%3D%22")
        # Proxy
        proxy: str = os.getenv("DOUYIN_PROXY", None)

    # ChatGPT API 设置 | ChatGPT API settings
    class ChatGPTSettings:
        # OpenAI API Key
        API_Key: str = os.getenv("OPENAI_API_KEY", "")
        # OpenAI ChatGPT Model
        GPT_Model: str = "gpt-3.5-turbo"

    # TikHub.io API 设置 | TikHub.io API settings
    class TikHubAPISettings:
        # TikHub.io API URL
        api_domain: str = "https://api.tikhub.io"
        # TikHub.io API Token
        api_key: str = os.getenv("TIKHUB_API_KEY", "")

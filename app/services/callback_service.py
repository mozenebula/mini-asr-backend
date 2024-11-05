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

import traceback
import datetime
from tenacity import *
from typing import Optional, Dict, Union
from app.database.DatabaseManager import DatabaseManager
from app.http_client.AsyncHttpClient import BaseAsyncHttpClient
from app.utils.logging_utils import configure_logging
from app.database.models import Task

logger = configure_logging(__name__)


class CallbackService:
    def __init__(self):
        self.default_headers = {
            "User-Agent": "Fast-Powerful-Whisper-AI-Services-API/Callback (https://github.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API)"
        }

    # @retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
    async def task_callback_notification(self,
                                         task: Task,
                                         db_manager: DatabaseManager,
                                         proxy_settings: Optional[Dict[str, str]] = None,
                                         method: str = "POST",
                                         headers: Optional[dict] = None,
                                         request_timeout: int = 10
                                         ) -> None:
        """
        发送任务处理结果的回调通知。

        Sends a callback notification with the result of the task processing.

        :param task: 要发送回调通知的任务实例 | Task instance to send callback notification for
        :param db_manager: 数据库管理器实例 | Database manager instance
        :param proxy_settings: 可选的代理设置 | Optional proxy settings
        :param method: 可选的请求方法 | Optional request method
        :param headers: 可选的请求头 | Optional request headers
        :param request_timeout: 请求超时时间 | Request timeout
        :return: None
        """
        callback_url = task.callback_url
        headers = headers or self.default_headers
        if callback_url:
            # TODO: 客户端在某些情况下可能会被关闭，需要进一步处理 2024年11月5日01:42:23
            async with BaseAsyncHttpClient(
                    proxy_settings=proxy_settings,
                    headers=headers,
                    request_timeout=request_timeout
            ).aclient as client:
                task_data = await db_manager.get_task(task.id)
                logger.info(f"Sending task callback notification for task {task.id} to: {callback_url}")

                response = await client.fetch_data(
                    url=callback_url,
                    method=method,
                    headers=headers,
                    json=task_data.to_dict()
                )

                if response:
                    logger.info(
                        f"Task callback notification sent successfully with response status: {response.status_code}")
                else:
                    logger.warning(
                        f"Task callback notification sent, but received empty response for task {task.id}")
        else:
            logger.info(f"No callback URL provided for task {task.id}, skipping callback notification.")


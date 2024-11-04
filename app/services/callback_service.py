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
from typing import Optional, Dict, Union
from app.database.SqliteDatabase import SqliteDatabaseManager
from app.database.MySQLDatabase import MySQLDatabaseManager
from app.http_client.AsyncHttpClient import BaseAsyncHttpClient
from app.utils.logging_utils import configure_logging
from app.database.models import Task

logger = configure_logging(__name__)


class CallbackService:
    def __init__(self):
        self.default_headers = {
            "User-Agent": "Fast-Powerful-Whisper-AI-Services-API/Callback (https://github.com/Evil0ctal/Fast-Powerful-Whisper-AI-Services-API)"
        }

    async def task_callback_notification(self,
                                         task: Task,
                                         db_manager: Union[SqliteDatabaseManager, MySQLDatabaseManager],
                                         proxy_settings: Optional[Dict[str, str]] = None,
                                         method: str = "POST",
                                         headers: Optional[dict] = None) -> None:
        """
        发送任务处理结果的回调通知。

        Sends a callback notification with the result of the task processing.

        :param task: 要发送回调通知的任务实例 | Task instance to send callback notification for
        :param db_manager: 数据库管理器实例 | Database manager instance
        :param proxy_settings: 可选的代理设置 | Optional proxy settings
        :param method: 可选的请求方法 | Optional request method
        :param headers: 可选的请求头 | Optional request headers
        :return: None
        """
        headers = headers or self.default_headers
        callback_url = task.callback_url
        try:
            async with BaseAsyncHttpClient(proxy_settings=proxy_settings, headers=headers) as client:
                task_data = await db_manager.get_task(task.id)
                logger.info(f"Sending task callback notification for task {task.id} to: {callback_url}")

                response = await client.fetch_data(
                    url=callback_url,
                    method=method,
                    headers=headers,
                    json=task_data.to_dict()
                )

                if response:
                    logger.info(f"Task callback notification sent successfully with response status: {response.status_code}")
                else:
                    logger.warning(f"Task callback notification sent, but received empty response for task {task.id}")

                # 更新任务的回调状态码、回调消息和回调时间
                # Update the task's callback status code, callback message, and callback time
                await db_manager.update_task_callback_status(
                    task_id=task.id,
                    callback_status_code=response.status_code,
                    callback_message=response.text[:512] if response else None,
                    callback_time=datetime.datetime.now()
                )

        except Exception as e:
            logger.error(f"Error sending task callback notification for task {task.id} to {callback_url}: {str(e)}")
            logger.debug(traceback.format_exc())


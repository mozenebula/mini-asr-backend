# ==============================================================================
# Copyright (C) 2021 Evil0ctal
#
# This file is part of the Douyin_TikTok_Download_API project.
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
# 　　　　 　　  ＿＿
# 　　　 　　 ／＞　　フ
# 　　　 　　| 　_　 _ l
# 　 　　 　／` ミ＿xノ
# 　　 　 /　　　 　 |       Feed me Stars ⭐ ️
# 　　　 /　 ヽ　　 ﾉ
# 　 　 │　　|　|　|
# 　／￣|　　 |　|　|
# 　| (￣ヽ＿_ヽ_)__)
# 　＼二つ
# ==============================================================================
#
# Contributor Link:
# https://github.com/Evil0ctal]
#
# ==============================================================================

import asyncio  # Asynchronous I/O 异步I/O
import time  # Time operations 时间操作
from urllib.parse import urlencode

from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_fixed  # Retry mechanism 重试机制

# Base crawler and TikTok API endpoints
from app.crawlers.base_crawler import BaseCrawler
from app.crawlers.platforms.example_tiktok.endpoints import TikTokAPIEndpoints
from app.crawlers.platforms.example_tiktok.models import FeedVideoDetail


def model_to_query_string(model: BaseModel) -> str:
    """
    Convert a Pydantic model to a URL query string.
    将 Pydantic 模型转换为 URL 查询字符串。
    """
    return urlencode(model.dict())


class TikTokAPPCrawler:
    """
    TikTok API crawler class to fetch TikTok video details.
    TikTok API 爬虫类，用于获取 TikTok 视频详情。
    """

    async def get_tiktok_headers(self) -> dict:
        """
        Generate request headers for TikTok API.
        生成 TikTok API 的请求头。
        """
        return {
            "headers": {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
                ),
                "Referer": "https://www.tiktok.com/",
                "Cookie": "ExampleCookie=HelloFromEvil0ctal",
                "x-ladon": "Hello From Evil0ctal!",
            },
            "proxies": {"http://": None, "https://": None},
        }

    @retry(stop=stop_after_attempt(10), wait=wait_fixed(1))
    async def fetch_one_video(self, aweme_id: str) -> dict:
        """
        Fetch a single TikTok video data by video ID (aweme_id).
        根据视频 ID (aweme_id) 获取单个 TikTok 视频数据。
        """
        # Retrieve headers and construct request parameters
        headers = await self.get_tiktok_headers()
        params = FeedVideoDetail(aweme_id=aweme_id)
        param_str = model_to_query_string(params)
        url = f"{TikTokAPIEndpoints.HOME_FEED}?{param_str}"

        # Create and use base crawler client to fetch video data
        async with BaseCrawler(proxies=headers["proxies"], crawler_headers=headers["headers"]) as crawler:
            response = await crawler.fetch_get_json(url)
            video_data = response.get("aweme_list", [{}])[0]

            # Verify if the fetched video ID matches the requested video ID
            if video_data.get("aweme_id") != aweme_id:
                raise ValueError("Invalid video ID (作品 ID 错误)")
        return video_data

    async def main(self):
        """
        Main function for testing single video data fetch.
        主函数，用于测试获取单个作品数据。
        """
        aweme_id = "7339393672959757570"
        response = await self.fetch_one_video(aweme_id)
        print(response)


if __name__ == "__main__":
    # Initialize TikTokAPPCrawler instance
    crawler = TikTokAPPCrawler()

    # Measure time taken for the fetch operation
    start_time = time.time()
    asyncio.run(crawler.main())
    end_time = time.time()

    print(f"耗时 (Duration): {end_time - start_time:.2f} 秒")

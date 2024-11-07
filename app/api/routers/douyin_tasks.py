import traceback
from typing import Union

from fastapi import Request, APIRouter, HTTPException, Form, status

from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel
from app.api.models.DouyinTaskRequest import DouyinVideoTask
from app.api.models.WhisperTaskRequest import WhisperTaskFileOption
from app.api.routers.whisper_tasks import task_create
from app.crawlers.platforms.douyin.crawler import DouyinWebCrawler
from app.utils.logging_utils import configure_logging

DouyinWebCrawler = DouyinWebCrawler()

router = APIRouter()

# 配置日志记录器
logger = configure_logging(name=__name__)


# 爬取抖音视频并创建任务 | Crawl Douyin video and create task
@router.post("/video_task",
             response_model=ResponseModel,
             summary="创建任务 / Create task",
             response_description="创建任务的结果信息 / Result information of creating a task"
             )
async def create_tiktok_video_task(
        request: Request,
        _DouyinVideoTask: DouyinVideoTask = Form(...),
) -> Union[ResponseModel, ErrorResponseModel]:
    """
    # [中文]

    ### 用途说明:
    - 通过抖音视频链接爬取视频并创建任务。

    ### 请求参数:
    - `url`: 抖音 视频链接，例如: `https://v.douyin.com/iANRkr9m/`。
    - 其他参数与创建任务时的参数相同。

    ### 返回结果:
    - 返回创建任务的结果信息。

    ### 错误代码说明:

    - `400`: 抖音视频抓取失败。
    - `500`: 未知错误。

    # [English]

    ### Description:
    - Crawl the video through the Douyin video link and create a task.

    ### Request parameters:
    - `url`: Douyin video link, for example: `https://v.douyin.com/iANRkr9m/`.
    - Other parameters are the same as when creating a task.

    ### Return result:
    - Return the result information of creating a task.

    ### Error code description:

    - `400`: Douyin video crawl failed.
    - `500`: Unknown error.
    """
    try:
        url = str(_DouyinVideoTask.url)
        platform = str(_DouyinVideoTask.platform)
        data = await DouyinWebCrawler.fetch_one_video_by_url(url)

        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Douyin video URL",
                headers={"X-Error": "Invalid Douyin video URL"}
            )
        else:
            # $.aweme_detail.video.play_addr.url_list.[2]
            url = data.get("aweme_detail", {}).get("video", {}).get("play_addr", {}).get("url_list", [])[-1]
            print(f"Video URL: {url}")

        # 创建任务 | Create task
        task_data = WhisperTaskFileOption(file_url=url, platform=platform)
        task_result = await task_create(
            request=request,
            file_upload=None,
            task_data=task_data
        )
        return task_result

    except HTTPException as http_error:
        raise http_error

    except Exception as error:
        logger.error(f"An error occurred: {error}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponseModel(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"An unexpected error occurred while creating the transcription task: {str(error)}",
                router=str(request.url),
                params=dict(request.query_params),
            ).model_dump()
        )

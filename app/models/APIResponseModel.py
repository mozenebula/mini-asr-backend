import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


# 创建一个通用的响应模型 | Create a common response model
class ResponseModel(BaseModel):
    code: int = Field(default=200, description="HTTP status code | HTTP状态码")
    router: str = Field(default="", description="The endpoint that generated this response | 生成此响应的端点")
    params: Any = Field(default={}, description="The parameters used in the request | 请求中使用的参数")
    data: Optional[Any] = Field(default=None, description="The response data | 响应数据")


# 定义错误响应模型 | Define an error response model
class ErrorResponseModel(BaseModel):
    code: int = Field(default=400, description="HTTP status code/HTTP状态码")
    message: str = Field(
        default="An error occurred. | 服务器发生错误。",
        description="Error message | 错误消息")
    time: str = Field(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                      description="The time the error occurred | 发生错误的时间")
    router: str = Field(default="", description="The endpoint that generated this response | 生成此响应的端点")
    params: dict = Field(default={}, description="The parameters used in the request | 请求中使用的参数")

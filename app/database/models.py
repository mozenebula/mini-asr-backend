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

import enum
import datetime as dt
from typing import Optional

from pydantic import BaseModel, constr, Field, ConfigDict, field_validator
from sqlalchemy import Column, Integer, String, Enum, Text, JSON, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

# 定义基础类 | Define Base class
Base = declarative_base()


# 定义任务状态的枚举类型 | Define an enum for task status
class TaskStatus(enum.Enum):
    QUEUED = 'queued'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'


# 定义任务优先级的枚举类型 | Define an enum for task priority
class TaskPriority(enum.Enum):
    # 1 - 低 | Low
    LOW = 'low'
    # 2 - 中 | Medium
    NORMAL = 'normal'
    # 3 - 高 | High
    HIGH = 'high'


class Task(Base):
    __tablename__ = 'tasks'

    # 任务ID | Task ID
    id = Column(Integer, primary_key=True)
    # 任务类型 | Task type
    task_type = Column(String, nullable=False)
    # 任务优先级 | Task priority
    priority = Column(Enum(TaskPriority), default=TaskPriority.NORMAL)
    # 任务状态，初始为 QUEUED | Task status, initially QUEUED
    status = Column(Enum(TaskStatus), default=TaskStatus.QUEUED)
    # 检测到的语言 | Detected language
    language = Column(String, nullable=True)
    # 引擎名称 | Engine name
    engine_name = Column(String, nullable=True)
    # 创建日期 | Creation date
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    # 更新时间 | Update date
    updated_at = Column(DateTime, onupdate=dt.datetime.utcnow)
    # 处理任务花费的总时间 | Total time spent processing the task
    task_processing_time = Column(Float, nullable=True)

    # 文件路径 | File path
    file_path = Column(String, nullable=False)
    # 文件名称 | File name
    file_name = Column(String, nullable=False)
    # 文件大小 | File size
    file_size_bytes = Column(Integer)
    # 音频时长 | Audio duration
    file_duration = Column(Float)

    # 解码选项 | Decode options
    decode_options = Column(JSON)

    # 结果 | Result
    result = Column(JSON, nullable=True)
    # 错误信息 | Error message
    error_message = Column(Text, nullable=True)
    # 输出结果链接 | Output URL
    output_url = Column(String, nullable=True)

    # 转换为字典 | Convert to dictionary
    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status.value,
            'priority': self.priority,
            'engine_name': self.engine_name,
            'task_type': self.task_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'task_processing_time': self.task_processing_time,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size_bytes': self.file_size_bytes,
            'file_duration': self.file_duration,
            'language': self.language,
            'decode_options': self.decode_options,
            'error_message': self.error_message,
            'output_url': self.output_url,
            'result': self.result
        }


# 查询任务的可选过滤器 | Query tasks optional filter
class QueryTasksOptionalFilter(BaseModel):
    status: Optional[TaskStatus] = Field(TaskStatus.COMPLETED, description="任务状态，例如 'queued' 或 'completed'")
    priority: Optional[TaskPriority] = Field(TaskPriority.NORMAL, description="任务优先级，例如 'low', 'normal', 'high'")
    created_after: Optional[str] = Field('', description="创建时间的起始时间，格式为 'YYYY-MM-DDTHH:MM:SS'")
    created_before: Optional[str] = Field('', description="创建时间的结束时间，格式为 'YYYY-MM-DDTHH:MM:SS'")
    language: Optional[constr(strip_whitespace=True, min_length=0, max_length=5)] = Field("", description="检测到的语言代码，空字符串表示不限制语言")
    engine_name: Optional[constr(strip_whitespace=True, max_length=50)] = Field("faster_whisper", description="引擎名称，例如 'faster_whisper'")
    has_result: Optional[bool] = Field(True, description="是否要求任务有结果")
    has_error: Optional[bool] = Field(False, description="是否要求任务存在错误信息")
    limit: int = Field(20, description="每页记录数，默认值为20")
    offset: int = Field(0, description="分页的起始位置，默认值为0")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # 自动将空字符串转换为 None | Automatically convert empty strings to None
    @field_validator("created_after", "created_before", "language", mode="before")
    def empty_str_to_none(cls, v):
        return None if v == "" else v

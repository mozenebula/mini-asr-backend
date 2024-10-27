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
#
# Contributor Link, Thanks for your contribution:
#
# No one yet...
#
# ==============================================================================

import enum
import datetime
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
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'


class Task(Base):
    __tablename__ = 'tasks'

    # 任务ID | Task ID
    id = Column(Integer, primary_key=True)
    # 创建日期 | Creation date
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # 更新时间 | Update date
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)
    # 任务状态，初始为 QUEUED | Task status, initially QUEUED
    status = Column(Enum(TaskStatus), default=TaskStatus.QUEUED)
    # 文件路径 | File path
    file_path = Column(String, nullable=False)
    # 文件名称 | File name
    file_name = Column(String, nullable=False)
    # 文件大小 | File size
    file_size_bytes = Column(Integer)
    # 音频时长 | Audio duration
    duration = Column(Float)
    # 解码选项 | Decode options
    decode_options = Column(JSON)
    # 结果 | Result
    result = Column(JSON, nullable=True)
    # 错误信息 | Error message
    error_message = Column(Text, nullable=True)
    # 尝试次数 | Attempts
    attempts = Column(Integer, default=0)
    # 任务优先级 | Task priority
    priority = Column(Enum(TaskPriority), default=TaskPriority.NORMAL)
    # 输出结果链接 | Output URL
    output_url = Column(String, nullable=True)
    # 检测到的语言 | Detected language
    language = Column(String, nullable=True)
    # 任务进度 | Task progress
    progress = Column(Float, default=0.0)

    # 转换为字典 | Convert to dictionary
    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'status': self.status.value,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size_bytes': self.file_size_bytes,
            'duration': self.duration,
            'decode_options': self.decode_options,
            'result': self.result,
            'error_message': self.error_message,
            'attempts': self.attempts,
            'priority': self.priority,
            'output_url': self.output_url,
            'language': self.language,
            'progress': self.progress
        }

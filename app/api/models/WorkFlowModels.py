from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum


# 定义触发类型的枚举 | Define an enum for trigger type
class TriggerType(str, Enum):
    MANUAL = 'MANUAL'
    SCHEDULED = 'SCHEDULED'
    EVENT = 'EVENT'


class WorkflowTaskSchema(BaseModel):
    TASK_ID: str
    COMPONENT: str
    PARAMETERS: Optional[Dict[str, Any]] = None
    RETRY_POLICY: Optional[Dict[str, int]] = None
    TIMEOUT: Optional[int] = 60
    DELAY: Optional[int] = 10
    CONDITION: Optional[Dict[str, Any]] = None
    DEPENDENCIES: Optional[List[str]] = None
    PRIORITY: str = "NORMAL"  # 使用字符串


class NotifyOnCompletionSchema(BaseModel):
    channel: str
    recipient: str
    message: str


class WorkflowSchema(BaseModel):
    WORKFLOW_NAME: str
    DESCRIPTION: Optional[str] = None
    TRIGGER_TYPE: TriggerType  # 使用触发类型枚举
    CALLBACK_URL: Optional[str] = None
    NOTIFY_ON_COMPLETION: Optional[NotifyOnCompletionSchema] = None
    tasks: List[WorkflowTaskSchema]

    def to_dict(self):
        # 将模型转换为字典，并手动转换枚举值为字符串
        data = self.dict()
        data['TRIGGER_TYPE'] = self.TRIGGER_TYPE.value  # 转换为字符串
        return data

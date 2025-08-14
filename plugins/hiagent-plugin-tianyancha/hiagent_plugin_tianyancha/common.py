from pydantic import BaseModel
from typing import Generic, TypeVar
from datetime import datetime

Result = TypeVar('Result')

class CommonResp(BaseModel, Generic[Result]):
    error_code: int
    reason: str
    result: Result | None = None

def timestamp_to_str(timestamp: int | None) -> str:
    if timestamp is None or timestamp <= 0:
        return ""
    return datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")

from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class OpenAIConfig(BaseModel):
    """存储配置"""
    model_config = ConfigDict(frozen=True)
    base_url: str = ""
    api_key: str = ""
    model_name: str = ""
    rpm: int = 5

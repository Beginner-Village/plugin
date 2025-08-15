from typing import BinaryIO
from datetime import datetime
from functools import cache
from pydantic import BaseModel, Field, ConfigDict

from hiagent_plugin_sdk.extensions.storage.base import BaseStorage

class LocalStorageConfig(BaseModel):
    """S3配置"""
    model_config = ConfigDict(frozen=True)

    base_dir: str = Field(default="/tmp", description="本地存储的路径")

    @cache
    def get_client(self):
        return LocalPathStorage(self)

class LocalPathStorage(BaseStorage):
    def __init__(self, cfg: LocalStorageConfig):
        self.base_dir = cfg.base_dir

    def save(self, filename: str, data: BinaryIO, length: int = -1, size: int = -1) -> str:
        with open(f"{self.base_dir}/{filename}", "wb") as f:
            for chunk in data:
                f.write(chunk)
        return f"file://{self.base_dir}/{filename}"

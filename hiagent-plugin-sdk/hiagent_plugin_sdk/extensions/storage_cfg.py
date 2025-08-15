from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
from hiagent_plugin_sdk.extensions.storage.base import BaseStorage
from hiagent_plugin_sdk.extensions.storage.minio_s3 import S3StorageConfig
from hiagent_plugin_sdk.extensions.storage.local import LocalStorageConfig


class StorageConfig(BaseModel):
    """存储配置"""
    model_config = ConfigDict(frozen=True)

    backend: Literal["local_path", "minio", "boto3"] = Field(default="local_path", description="对象存储的 access key")
    local_path: LocalStorageConfig | None = Field(default_factory=LocalStorageConfig, description="本地存储的配置")
    s3: S3StorageConfig | None = Field(default=None, description="s3 存储的配置")

    def get_client(self) -> BaseStorage:
        match self.backend:
            case "local_path":
                if self.local_path is None:
                    raise ValueError("local_path is None")
                return self.local_path.get_client()
            case "minio":
                if self.s3 is None:
                    raise ValueError("minio is None")
                return self.s3.get_minio_client()
            case "boto3":
                if self.s3 is None:
                    raise ValueError("minio is None")
                return self.s3.get_boto3_client()

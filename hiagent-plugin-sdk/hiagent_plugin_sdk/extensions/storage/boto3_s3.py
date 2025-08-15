from typing import BinaryIO
from datetime import datetime
from functools import cache
from pydantic import BaseModel, Field, ConfigDict
from minio import Minio
from uuid import uuid4
import json

from hiagent_plugin_sdk.extensions.storage.base import BaseStorage

class S3StorageConfig(BaseModel):
    """S3配置"""
    model_config = ConfigDict(frozen=True)

    ak: str = Field(default="", description="对象存储的 access key")
    sk: str = Field(default="", description="对象存储的 secret key")
    endpoint: str = Field(default="", description="对象存储的 endpoint")
    region: str = Field(default="", description="对象存储所在的 region")
    bucket: str = Field(default="", description="对象存储使用的 bucket")
    public_endpoint: str = Field(default="", description="对象存储的公开访问地址")
    path_style: bool = Field(
        default=False, description="是否使用 xxxx/${bucket_name}/xxxx 格式"
    )
    ssl_verify: bool = Field(default=True, description="是否校验对象存储服务的证书")

    @cache
    def get_client(self):
        return MinioS3Storage(self)

class MinioS3Storage(BaseStorage):
    def __init__(self, cfg: S3StorageConfig):
        self.bucket = cfg.bucket
        self.public_endpoint = cfg.public_endpoint
        self.endpoint = cfg.endpoint
        if cfg.endpoint.startswith("https://"):
            endpoint = cfg.endpoint.removeprefix("https://")
            secure = True
        elif cfg.endpoint.startswith("http://"):
            endpoint = cfg.endpoint.removeprefix("http://")
            secure = False
        else:
            secure = True

        if not cfg.path_style:
            endpoint = f"{cfg.bucket}.{endpoint}"

        self.client = Minio(
            endpoint=endpoint,
            region=cfg.region,
            access_key=cfg.ak,
            secret_key=cfg.sk,
            secure=secure,
            cert_check=cfg.ssl_verify,
        )
        if not self.client.bucket_exists(cfg.bucket):
            self.client.make_bucket(cfg.bucket)
            policy_read_only = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket}/*"],
                    }
                ],
            }
            self.client.set_bucket_policy(self.bucket, json.dumps(policy_read_only))

    def save(self, filename: str, data: BinaryIO, length=-1, size=-1) -> str:
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        uuid = uuid4().hex
        dst_path = f"{year}/{month}/{day}/{uuid}/{filename}"
        file_extension = filename.split(".")[-1]
        match file_extension:
            case "jpg" | "jpeg" | "png" | "gif" | "webp":
                content_type = f"image/{file_extension}"
            case "mp3" | "wav" | "ogg":
                content_type = f"audio/{file_extension}"
            case "svg":
                content_type = "image/svg+xml"
            case "pdf":
                content_type = "application/pdf"
            case "txt":
                content_type = "text/plain"
            case _:
                content_type = "application/octet-stream"
        # if size < 5 * 1024 **2:
        #     size = 5 * 1024 **2
        _ = self.client.put_object(
            bucket_name=self.bucket,
            object_name=dst_path,
            data=data,
            length=length,
            content_type=content_type,
            # part_size=size,
        )
        return f'{self.public_endpoint}/{self.bucket}/{dst_path}'

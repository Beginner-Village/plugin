import asyncio
import enum
from typing import Annotated
import os
import io
from pathlib import Path

import aiohttp
from pydantic import Field

from hiagent_plugin_sdk import BasePlugin, set_meta, ConfigValidateMixin, SecretField, BuiltinCategory, arequest
from hiagent_plugin_sdk.extensions import load

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

class VectorizerMode(enum.Enum):
    production = "production"
    """This mode is intended for production use and all parameters are supported."""
    preview = "preview"
    """This mode is intended for when you want to show your end-user a preview before they make a purchase. It produces a 4x PNG result with a discreet watermark, ignoring any contradictory parameters."""
    test = "test"
    """This modes are intended for developer use when integrating with the service. All parameters are supported, but there's significant watermarking."""
    test_preview = "test_preview"
    """This modes are intended for developer use when integrating with the service. All parameters are supported, but there's significant watermarking."""


@set_meta(cn_name="Vectorizer.AI")
class VectorizerAIPlugin(BasePlugin, ConfigValidateMixin):
    """一个将 PNG 和 JPG 图像快速轻松地转换为 SVG 矢量图的工具。"""
    hiagent_tools = ["vectorize"]
    hiagent_category = BuiltinCategory.ImageProcessing

    def __init__(
        self,
        api_key_name: Annotated[str, Field(title="Vectorizer.AI API Name", description="如何获取: https://vectorizer.ai/api")],
        api_key_value: Annotated[str, SecretField(title="Vectorizer.AI API Key", description="如何获取: https://vectorizer.ai/api")],
        mode: Annotated[str, Field(title="模式", description="test：测试模式（默认，可以免费测试API），test_preview：测试预览模式，production：生产模式，preview：预览模式")] = "test"
    ):
        if not mode:
            mode = VectorizerMode.test.value
        self.api_key_name = api_key_name
        self.api_key_value = api_key_value
        self.mode = mode

    async def _validate(self):
        if not self.api_key_name:
            raise ValueError("api_key_name is empty")
        if not self.api_key_value:
            raise ValueError("api_key_value is empty")
        if not self.mode:
            raise ValueError("mode is empty")
        if not hasattr(VectorizerMode, self.mode):
            raise ValueError(f"mode {self.mode} is not supported")

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    async def vectorize(
        self,
        image_url: Annotated[str, Field(title="图片URL", description="要转换图片的URL")]
    ):
        """一个将 PNG 和 JPG 图像快速轻松地转换为 SVG 矢量图的工具。"""
        async with aiohttp.ClientSession(trust_env=True, timeout=aiohttp.ClientTimeout(total=60)) as session:
            async with session.get(image_url, allow_redirects=True) as resp_img:
                resp_img.raise_for_status()
                data = await resp_img.content.read()
                image_binary = io.BytesIO(data)

                async with session.post(
                    "https://vectorizer.ai/api/v1/vectorize",
                    data=aiohttp.FormData(fields={
                        "image": image_binary,
                        "mode": self.mode
                    }),
                    auth=aiohttp.BasicAuth(login=self.api_key_name, password=self.api_key_value),
                    allow_redirects=True
                ) as resp_svg:
                    resp_svg.raise_for_status()
                    data = await resp_svg.content.read()
                    f = io.BytesIO(data)
                    # print(f"data: {len(data)}")
                    storage = load().storage.get_client()
                    return await asyncio.to_thread(storage.save, "vectorize.svg", f, length=len(data))

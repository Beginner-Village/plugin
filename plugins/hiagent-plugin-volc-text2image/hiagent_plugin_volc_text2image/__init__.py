
from typing import Any, Optional, List, Dict, Annotated, Literal
import base64
import os
from io import BytesIO
from pathlib import Path
import json
import asyncio
from functools import partial
from pydantic import BaseModel, Field
from volcenginesdkcore.signv4 import SignerV4 # type: ignore
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory, arequest
from hiagent_plugin_sdk.extensions import load
from hiagent_plugin_volc_text2image.common import VolcResp, VolcAPIException, ImageResult

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

@set_meta(cn_name="文生图")
class VolcText2Image(BasePlugin):
    """根据文本描述生成图像，单次仅支持生成一张图片"""
    hiagent_tools = ["text2image"]
    hiagent_category = BuiltinCategory.ImageProcessing

    HOST = "visual.volcengineapi.com"
    HOST_ADDR = f"https://{HOST}"

    def __init__(self,
        access_key: Annotated[str, Field(description="申请链接: https://console.volcengine.com/iam/keymanage/")],
        secret_key: Annotated[str, SecretField(description="申请链接: https://console.volcengine.com/iam/keymanage/")],
    ) -> None:
        self.ak = access_key
        self.sk = secret_key
        self.storage = load().storage.get_client()

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    # https://www.volcengine.com/docs/6791/1339374#%E6%8E%A5%E5%8F%A3%E7%AE%80%E4%BB%8B
    async def text2image(self,
        prompt: Annotated[str, Field(title="提示词", description="用于生成图像的提示词 ，中英文均可输入")],
        width: Annotated[int, Field(description="生成图像的宽，取值范围[256-768]", ge=256, le=768)] = 512,
        height: Annotated[int, Field(description="生成图像的高，取值范围[256-768]",ge=256, le=768)] = 512,
        use_sr: Annotated[bool, Field(description="内置的超分功能，开启后可将上述宽高均乘以2返回，此参数打开后延迟会有增加")] = False,
    ) -> ImageResult:
        """通过文字描述生成图片，一次只能生成一张图片。"""
        version = "2022-08-31"
        action = "CVProcess"
        params = {
            "Action": action,
            "Version": version,
        }
        service = "cv"
        region = "cn-north-1"
        headers = {
            "Content-Type": "application/json",
            "Host": self.HOST,
            "Service": service,
            "Region": region,
            "Version": version,
        }
        body = {
            "prompt": prompt,
            "req_key": "high_aes_general_v20_L",
            "width": width,
            "height": height,
            "use_sr": use_sr,
        }
        SignerV4.sign(
            path="/",
            method="POST",
            headers=headers,
            body=json.dumps(body),
            post_params=None,
            query=params,
            ak=self.ak,
            sk=self.sk,
            region=region,
            service=service,
        )
        async with arequest("POST", self.HOST_ADDR, json=body, headers=headers, params=params) as resp:
            resp_dict = await resp.json()
        # with open("./tests/resp.json", "w", encoding="utf-8") as f:
        #     json.dump(resp_dict, f, ensure_ascii=False, indent=2)
        data = VolcResp(**resp_dict)
        if data.code != 10000:
            raise VolcAPIException(data.code, data.message)
        if data.data is None:
            raise VolcAPIException(-1, "response data is None")
        if len(data.data.binary_data_base64) == 0:
            raise VolcAPIException(-1, "response data.binary_data_base64 is empty")
        image_url = await self._save_image(data.data.binary_data_base64[0])
        return ImageResult(
            image_url=image_url,
            rephraser_result=data.data.rephraser_result,
            pe_result=data.data.pe_result,
        )

    async def _save_image(self, base64_data: str) -> str:
        image = base64.standard_b64decode(base64_data)
        f = BytesIO(image)
        length = len(image)
        return await asyncio.to_thread(partial(self.storage.save, f"{md5(base64_data)[:10]}/image.png", f, length=length))

def md5(data):
    import hashlib
    md5 = hashlib.md5()
    md5.update(data.encode('utf-8'))
    return md5.hexdigest()

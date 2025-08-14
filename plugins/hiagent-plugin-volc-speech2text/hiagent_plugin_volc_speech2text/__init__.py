
from typing import Any, Optional, List, Dict, Annotated, Literal
import os
import logging
from pathlib import Path
import aiofiles as aiof
from urllib.parse import urlparse
from pydantic import BaseModel, Field
from hiagent_plugin_sdk import BasePlugin, ConfigValidateMixin, set_meta, SecretField, BuiltinCategory, arequest
from hiagent_plugin_volc_speech2text.client import AsrWsClient

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger(__name__)
class VolcException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Volc error: code={code}, message={message}")

@set_meta(cn_name="录音文件识别")
class VolcSpeech2Text(BasePlugin, ConfigValidateMixin):
    """录音文件识别是一个提取语音文本的插件，仅支持识别 raw / wav / ogg / mp3 格式的音频文件"""
    hiagent_tools = ["SpeechToText"]
    hiagent_category = BuiltinCategory.AudioVideo

    def __init__(self,
        app_id: Annotated[str, Field(title="app_id", description="申请说明: <https://www.volcengine.com/docs/6561/80818>")],
        token: Annotated[str, SecretField(title="token")],
        cluster: Annotated[str, Field(title="业务集群", description="根据场景，选择需要访问的集群。")],
    ) -> None:
        self.app_id = app_id
        self.token = token
        self.cluster = cluster

    def _validate(self):
        if not self.app_id:
            raise ValueError("app_id is empty")
        if not self.token:
            raise ValueError("token is empty")
        if not self.cluster:
            raise ValueError("cluster is empty")

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    # https://www.volcengine.com/docs/6561/80818
    async def SpeechToText(self,
        url: Annotated[str, Field(description="录音文件的url")],
        format: Annotated[Literal["wav, mp3", "ogg", "raw"], Field(description="录音文件格式, 支持的格式有: raw / wav / ogg / mp3 "), ],
    ) -> Annotated[str, Field(description="识别到的音频文件文字信息")]:
        """读取音频url链接，并将音频转为文字"""
        # TODO: 处理输出结构, 验证大文件的输出处理
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ["http", "https", "file"]:
            raise ValueError("url is invalid")

        if format == "ogg":
            codec = "opus"
        else:
            codec = "raw"
        if parsed_url.scheme == "file":
            if not Path(parsed_url.path).is_file():
                raise ValueError("file not found")
            cli = AsrWsClient(
                parsed_url.path, self.cluster, appid=self.app_id, token=self.token,
                format=format, codec=codec)
            data = await cli.execute()
        else:
            async with aiof.tempfile.NamedTemporaryFile() as f:
                async with arequest("GET", url) as resp:
                    resp.raise_for_status()
                    async for trunc in resp.content.iter_chunked(8192):
                        await f.write(trunc)
                    await f.flush()
                cli = AsrWsClient(
                    f.name, self.cluster,
                    appid=self.app_id, token=self.token, format=format, codec=codec)
                # {'payload_msg': {'addition': {'duration': '3264', 'logid': '20241125112235CACC2F564CDCB4F63A3C', 'split_time': '[]'}, 'code': 1000, 'message': 'Success', 'reqid': 'b25be66b-0cde-4af2-ae14-34458e91c06e', 'result': [{'confidence': 0, 'text': '测试语音识别。'}], 'sequence': -4}, 'payload_size': 237}
                data = await cli.execute()
        logger.debug(f"data: {data}")
        data = data.get("payload_msg", {})
        code = data.get("code", -1)
        message = data.get("message", "unknown")
        if code!= 1000:
            raise VolcException(code, message)
        result = data.get("result", [])
        if len(result) == 0:
            raise VolcException(0, "no result found")
        return result[0].get("text", "")

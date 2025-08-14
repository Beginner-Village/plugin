
from typing import Any, Optional, List, Dict, Annotated, Literal, Tuple
import os
import logging
from pathlib import Path
import json
import asyncio
import uuid
from pydantic import BaseModel, Field
from hiagent_plugin_sdk import BasePlugin, ConfigValidateMixin, set_meta, SecretField, arequest, BuiltinCategory
from hiagent_plugin_volc_speech2textllm.types import Resp

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger(__name__)
class VolcException(Exception):
    def __init__(self, code: str, message: str, logid: str):
        self.code = code
        self.message = message
        self.logid = logid
        super().__init__(f"Volc error: code={code}, message={message}, logid={logid}")

@set_meta(cn_name="火山大模型录音文件识别")
class VolcSpeech2Text(BasePlugin, ConfigValidateMixin):
    """录音文件识别是一个提取语音文本的插件，仅支持识别 raw / wav / ogg / mp3 格式的音频文件"""
    hiagent_tools = ["SpeechToText"]
    hiagent_category = BuiltinCategory.AudioVideo

    def __init__(self,
        app_id: Annotated[str, Field(title="app_id", description="申请说明: <https://www.volcengine.com/docs/6561/1354868>")],
        token: Annotated[str, SecretField(title="token")],
    ) -> None:
        self.app_id = app_id
        self.token = token

    def _validate(self):
        if not self.app_id:
            raise ValueError("app_id is empty")
        if not self.token:
            raise ValueError("token is empty")

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    # https://www.volcengine.com/docs/6561/1354868
    async def SpeechToText(self,
        url: Annotated[str, Field(description="录音文件的url")],
        format: Annotated[Literal["wav, mp3", "ogg", "raw"], Field(description="录音文件格式, 支持的格式有: raw / wav / ogg / mp3 ")],
        enable_speaker_info: Annotated[bool, Field(description="启用说话人聚类分离, 默认不开启")] = False,
        enable_itn: Annotated[bool, Field(description="启用文本规范化 (ITN), 默认开启")] = True,
        enable_ddc: Annotated[bool, Field(description="启用顺滑, 默认开启")] = True,
        enable_punc: Annotated[bool, Field(description="启用标点, 默认开启")] = True,
    ) -> Annotated[Resp, Field(description="识别到的音频文件文字信息")]:
        """读取音频url链接，并将音频转为文字"""
        addr = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit"
        req_id = str(uuid.uuid4())
        headers = {
            "X-Api-App-Key": self.app_id,
            "X-Api-Access-Key": self.token,
            "X-Api-Resource-Id": "volc.bigasr.auc",
            "X-Api-Request-Id": req_id,
            "X-Api-Sequence": "-1",
        }
        body = {
            "audio": {
                "url": url,
                "format": format,
            },
            "request": {
                "model_name": "bigmodel",
                "show_utterances": True,
                "enable_speaker_info": enable_speaker_info,
                "enable_itn": enable_itn,
                "enable_ddc": enable_ddc,
                "enable_punc": enable_punc,
            },
        }
        # print(json.dumps(body, indent=2, ensure_ascii=False))
        async with arequest("POST", addr, headers=headers, json=body) as resp:
            await resp.text()
            resp.raise_for_status()
            logid = resp.headers.getone("X-Tt-Logid", "")
            status_code = resp.headers.getone("X-Api-Status-Code", "")
            status_msg = resp.headers.getone("X-Api-Message", "")
            if status_code != "20000000":
                raise VolcException(status_code, status_msg, logid)
        # 每2s 查询一次
        loop, interval = 180, 2
        for i in range(loop):
            logger.debug(f"query result [{i}]: req_id={req_id}")
            ok, ret = await self._query(req_id)
            if ok:
                return ret
            await asyncio.sleep(interval)
        raise VolcException("-1", f"query result timeout for {loop*interval/60}min, req_id={req_id}", logid)

    async def _query(self, req_id: str) -> Tuple[bool, Resp]:
        addr = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/query"
        logger.info(f"addr={addr}, req_id={req_id}")
        headers = {
            "X-Api-App-Key": self.app_id,
            "X-Api-Access-Key": self.token,
            "X-Api-Resource-Id": "volc.bigasr.auc",
            "X-Api-Request-Id": req_id,
        }
        async with arequest("POST", addr, headers=headers, json={}) as resp:
            await resp.json()
            resp.raise_for_status()
            logid = resp.headers.getone("X-Tt-Logid", "")
            status_code = resp.headers.getone("X-Api-Status-Code", "-1")
            status_msg = resp.headers.getone("X-Api-Message", "")
            if status_code in ("20000001", "20000002"):
                return False, Resp()
            if status_code != "20000000":
                raise VolcException(status_code, status_msg, logid)
            ret_dict = await resp.json()
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret = Resp(**ret_dict)
        return True, ret


from typing import Any, Optional, List, Dict, Annotated, Literal, AsyncGenerator
import os
from pathlib import Path
import json
import logging
import io
from pydantic import BaseModel, Field
from volcenginesdkcore.signv4 import SignerV4 # type: ignore

from hiagent_plugin_sdk.schema import ServerSentEvent
from hiagent_plugin_sdk import BasePlugin, set_meta, set_tool_meta, SecretField, BuiltinCategory, arequest

from hiagent_plugin_volc_searchbot.common import SearchResp, VolcAPIException, VolcRespResult, AgentIntention
from hiagent_plugin_volc_searchbot.helper import adapter_runtime
from hiagent_plugin_volc_searchbot.ssedecoder import decode_sse

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


@set_meta(cn_name="联网内容搜索")
class VolcSearchBot(BasePlugin):
    """火山内容团队提供的联网内容搜索插件，背靠豆包大模型与联网内容智能体，适用于联网问答、新闻播报、行程规划等场景。"""
    hiagent_tools = ["SmartSearch"]
    hiagent_category = BuiltinCategory.WebSearch

    HOST= "mercury.volcengineapi.com"
    HOST_ADDR = f"https://{HOST}"

    def __init__(self,
        access_key: Annotated[str, Field(description="联网内容搜索功能由火山内容团队提供，背靠豆包大模型与联网内容智能体，请联系您的专属售前获取相关授权。")],
        secret_key: Annotated[str, SecretField(description="联网内容搜索功能由火山内容团队提供，背靠豆包大模型与联网内容智能体，请联系您的专属售前获取相关授权。")],
        bot_id: Annotated[str, Field(title="智能体ID")],
    ) -> None:
        self.ak = access_key
        self.sk = secret_key
        self.bot_id = bot_id

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    # https://bytedance.larkoffice.com/wiki/PPlZwYLNMigQA4kWgH8cEwJpn8f
    async def _SmartSearchStream(self, query: str) -> AsyncGenerator[ServerSentEvent, None]:
        req = self._build_request(query, stream=True)
        async with arequest("POST", self.HOST_ADDR, **req) as resp:
            resp.raise_for_status()
            logging.info(f"headers: {resp.headers}")
            async for line in resp.content:
                trunc = line.decode("utf-8")
                if resp.headers.get("content-type") == "text/event-stream":
                    # logging.debug(f'raw: {trunc}\n')
                    evt = decode_sse(trunc)
                    # print(f'event: {evt}\n')
                    if evt is not None:
                        yield evt
                elif resp.headers.get("content-type") == "application/json":
                    resp_json = json.loads(trunc)
                    result = VolcRespResult(**resp_json)
                    if result is None:
                        raise VolcAPIException(code="APIResponseError", message="result is None")
                    if result.error is not None:
                        raise VolcAPIException(code=result.error.code, message=result.error.message)
                else:
                    raise VolcAPIException(code="APIResponseError", message=f"unknown content: {trunc}")

    async def SmartSearch_stream(self,
        query: Annotated[str, Field(description="查询文本")],
    ) -> AsyncGenerator[ServerSentEvent, None]:
        """根据用户query，进行联网内容搜索"""
        async for evt in self._SmartSearchStream(query):
            for evt in adapter_runtime(evt):
                if evt is None:
                    continue
                yield evt

    # https://bytedance.larkoffice.com/wiki/PPlZwYLNMigQA4kWgH8cEwJpn8f
    @set_tool_meta(
        stream_fn="SmartSearch_stream",
        feat_runtime_intention=True,
    )
    async def SmartSearch(self,
        query: Annotated[str, Field(description="查询文本")],
    ) -> SearchResp:
        """根据用户query，进行联网内容搜索"""
        return await self.smart_search_by_stream(query)

    async def smart_search(self,
        query: Annotated[str, Field(description="查询文本")],
    ) -> SearchResp: # unused
        """根据用户query，进行联网内容搜索"""
        req = self._build_request(query, stream=False)
        async with arequest("POST", self.HOST_ADDR, **req) as resp:
            resp.raise_for_status()
            resp_json = await resp.json()
            # print(f"headers: {resp.headers}")
        # print(json.dumps(resp_json, ensure_ascii=False, indent=2))
        result = VolcRespResult(**resp_json)
        if result is None:
            raise VolcAPIException(code="APIResponseError", message="result is None")
        if result.error is not None:
            raise VolcAPIException(code=result.error.code, message=result.error.message)
        if len(result.choices) == 0:
            raise VolcAPIException(code="APIResponseError", message="result choices is empty")
        if result.choices[0].message is None:
            raise VolcAPIException(code="APIResponseError", message="result choices[0].message is None")
        content = result.choices[0].message.content
        ret = SearchResp(content=content)
        if len(result.references) > 0 or len(result.cards) > 0:
            ret.agent_intention = AgentIntention(
                references=result.references,
                cards=result.cards,
            )
        return ret

    async def smart_search_by_stream(self,
        query: Annotated[str, Field(description="查询文本")],
    ) -> SearchResp:
        """使用流式的接口封装非流式的返回"""
        g = self.SmartSearch_stream(query)
        resp = SearchResp(content="")
        contentIO = io.StringIO()
        async for evt in g:
            if evt.event == "message" and evt.data:
                data_dict = json.loads(evt.data)
                contentIO.write(data_dict.get("content", ""))
            elif evt.event == "agent_intention" and evt.data:
                data_dict = json.loads(evt.data)
                resp.agent_intention = AgentIntention(**data_dict)
        contentIO.flush()
        resp.content = contentIO.getvalue()
        contentIO.close()
        return resp

    def _build_request(self, query: str, stream: bool = False) -> dict:
        body = {
            "bot_id": self.bot_id,
            "messages": [{
                "role": "user",
                "content": query,
            }],
            "stream": stream,
        }
        version = "2024-01-01"
        params = {
            "Action":  "ChatCompletion",
            "Version": version,
        }
        service = "volc_torchlight_api"
        region = "cn-beijing"
        headers = {
                "Content-Type": "application/json",
                "Host": self.HOST,
                "Service": service,
                "Region": region,
                "Version": version,
            }
        SignerV4.sign(
            path="/",
            method="POST",
            headers=headers,
            post_params=None,
            body=json.dumps(body),
            query=params,
            ak=self.ak,
            sk=self.sk,
            region=region,
            service=service,
        )
        return {
            "headers": headers,
            "json": body,
            "params": params,
        }

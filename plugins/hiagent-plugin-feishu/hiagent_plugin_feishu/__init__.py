
from typing import Any, Optional, List, Dict, Annotated
import os
from pydantic import Field
from pathlib import Path
from hiagent_plugin_sdk import BasePlugin, ConfigValidateMixin, set_meta, SecretField, BuiltinCategory, assrf_request

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


@set_meta(cn_name="飞书")
class FeishuPlugin(BasePlugin, ConfigValidateMixin):
    """飞书群机器人"""
    hiagent_tools = ["feishu_group_bot"]
    hiagent_category = BuiltinCategory.Productivity

    def __init__(self,
        hook_key: Annotated[str, SecretField(title="群机器人webhook的key", description="详情见: https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot")],
        host: Annotated[str, Field(description="飞书接口域名, 默认: open.feishu.cn")] = "open.feishu.cn",
    ):
        self.hook_key = hook_key
        self.host = host or "open.feishu.cn"

    async def _validate(self):
        if not self.hook_key:
            raise ValueError("hook_key is empty")

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    # https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot
    async def feishu_group_bot(self,content: str) -> str:
        """发送群消息"""
        if self.host not in ["open.feishu.cn", "open.larkoffice.com"]:
            raise ValueError("host is invalid")

        api_url = f"https://{self.host}/open-apis/bot/v2/hook/{self.hook_key}"
        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "msg_type": "text",
            "content": {
                "text": content,
            },
        }

        async with assrf_request("POST", api_url, headers=headers, json=data) as resp:
            resp.raise_for_status()
            ret_dict = await resp.json()
        code = ret_dict.get("code")
        if code != 0:
            return f"Failed to send message to group chat bot.[{code}] {ret_dict.get('msg')}"
        return "Success"

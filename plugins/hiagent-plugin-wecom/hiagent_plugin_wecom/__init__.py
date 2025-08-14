import httpx
import uuid
from hiagent_plugin_sdk import BasePlugin, set_meta, BuiltinCategory
from typing import Any, Annotated
from pathlib import Path
from pydantic import Field
import os

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


@set_meta(cn_name="企业微信")
class WecomPlugin(BasePlugin):
    """企业微信群机器人"""
    hiagent_tools = ["wecom_robot_send"]
    hiagent_category = BuiltinCategory.Productivity

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def wecom_robot_send(
        self,
        content: Annotated[str, Field(description="消息内容")],
        hook_key: Annotated[str, Field(description="申请说明: <https://developer.work.weixin.qq.com/document/path/91770>")],
        message_type: Annotated[str, Field(description="消息类型，一般为 text")],
    ) -> str:
        """
        invoke tools
        """
        if content == '':
            return f"Invalid parameter content"

        print('打印', hook_key)

        if not self._is_valid_uuid(hook_key):
            return f"Invalid parameter hook_key ${hook_key}, not a valid UUID"

        if message_type == '':
            return f"Invalid parameter message_type"

        if message_type == "markdown":
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content,
                },
            }
        else:
            payload = {
                "msgtype": "text",
                "text": {
                    "content": content,
                },
            }
        api_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send"
        headers = {
            "Content-Type": "application/json",
        }
        params = {
            "key": hook_key,
        }

        try:
            res = httpx.post(api_url, headers=headers, params=params, json=payload)
            if res.is_success:
                return f"Text message sent successfully."
            else:
                return f"Failed to send the text message, res: {str(res.text)}"
        except Exception as e:
            return f"Failed to send message to group chat bot, error: {str(e)}"

    @staticmethod
    def _is_valid_uuid(uuid_str: str) -> bool:
        try:
            uuid.UUID(uuid_str)
            return True
        except Exception:
            return False

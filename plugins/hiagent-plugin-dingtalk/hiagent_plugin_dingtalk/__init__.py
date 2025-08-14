import os
import base64
import hashlib
import hmac
import logging
import time
import urllib.parse
from typing import Any, Annotated
from pathlib import Path
from pydantic import Field

import httpx

from hiagent_plugin_sdk import BasePlugin, set_meta, BuiltinCategory


current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


@set_meta(cn_name="钉钉")
class DingTalkPlugin(BasePlugin):
    """钉钉群机器人"""
    hiagent_tools = ["ding_robot_send"]
    hiagent_category = BuiltinCategory.Productivity

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def ding_robot_send(
        self,
        content: Annotated[str, Field(description="消息内容")],
        access_token: Annotated[str, Field(description="申请说明: <https://open.dingtalk.com/document/orgapp/custom-robot-access>")],
        sign_secret: Annotated[str, Field(description="申请说明: <https://open.dingtalk.com/document/robots/customize-robot-security-settings>")],
    ) -> str:
        """
        Dingtalk custom group robot API docs:
        https://open.dingtalk.com/document/orgapp/custom-robot-access
        """

        if content == '':
            return f"Invalid parameter content"

        if access_token == '':
            return f"Invalid parameter access_token"

        if sign_secret == '':
            return f"Invalid parameter sign_secret"

        msgtype = "text"
        api_url = "https://oapi.dingtalk.com/robot/send"
        headers = {
            "Content-Type": "application/json",
        }
        params = {
            "access_token": access_token,
        }

        self._apply_security_mechanism(params, sign_secret)

        payload = {
            "msgtype": msgtype,
            "text": {
                "content": content,
            },
        }

        try:
            res = httpx.post(api_url, headers=headers, params=params, json=payload)
            if res.is_success:
                return f"Text message sent successfully"
            else:
                return f"Failed to send the text message, res: {str(res.text)}"
        except Exception as e:
            return f"Failed to send message to group chat bot, error: {str(e)}"

    @staticmethod
    def _apply_security_mechanism(params: dict[str, Any], sign_secret: str):
        try:
            timestamp = str(round(time.time() * 1000))
            secret_enc = sign_secret.encode("utf-8")
            string_to_sign = f"{timestamp}\n{sign_secret}"
            string_to_sign_enc = string_to_sign.encode("utf-8")
            hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

            params["timestamp"] = timestamp
            params["sign"] = sign
        except Exception:
            msg = "Failed to apply security mechanism to the request."
            logging.exception(msg)

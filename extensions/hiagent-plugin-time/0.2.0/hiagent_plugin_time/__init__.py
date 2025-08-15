from typing import Annotated
import os
import datetime
from pathlib import Path
from pydantic import Field
from pytz import timezone as pytz_timezone
from hiagent_plugin_sdk import BasePlugin, set_meta, BuiltinCategory

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


@set_meta(cn_name="时间工具")
class TimePlugin(BasePlugin):
    """一个用于获取当前时间的工具。"""
    hiagent_tools = ["current_time"]
    hiagent_category = BuiltinCategory.Productivity

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    async def current_time(self,
        timezone: Annotated[str, Field(description="标准时区, 默认为UTC, 比如: Asia/Shanghai")] = "UTC"
    ) -> str:
        """获取当前时间"""
        if timezone == "":
            timezone = "UTC"
        t_format = "%Y-%m-%d %H:%M:%S %Z"
        tz = pytz_timezone(timezone)
        return datetime.datetime.now(tz).strftime(t_format)

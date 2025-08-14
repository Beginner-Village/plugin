from typing import Annotated, Any, Pattern, List
import os
import re
from pathlib import Path
from pydantic import Field
from hiagent_plugin_sdk import BasePlugin, set_meta, BuiltinCategory

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


@set_meta(cn_name="正则表达式提取")
class RegexPlugin(BasePlugin):
    """一个用于正则表达式内容提取的工具"""
    hiagent_tools = ["regex_extract"]
    hiagent_category = BuiltinCategory.Productivity

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    async def regex_extract(self,
        content: Annotated[str, Field(description="内容")],
        expression: Annotated[str | Pattern[str], Field(description="正则表达式")],
    ) -> List[str]:
        """一个用于利用正则表达式提取匹配内容结果的工具"""
        return re.findall(expression, content)

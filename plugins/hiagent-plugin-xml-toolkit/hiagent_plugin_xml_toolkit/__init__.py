
from typing import Annotated
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from pydantic import Field
from hiagent_plugin_sdk import BasePlugin, set_meta, BuiltinCategory, assrf_request

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


@set_meta(cn_name="xml工具")
class XmlToolkitPlugin(BasePlugin):
    """与 XML 规范交互的工具"""
    hiagent_tools = ["xml_spec_find_element"]
    hiagent_category = BuiltinCategory.Productivity

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"


    async def xml_spec_find_element(self,
        match: Annotated[str, Field(description='用于查找的 XML 标签名称或 XPath 表达式文本，（例如：.//year/..[@name="Singapore"]） ')],
        xml_file_url: Annotated[str, Field(description="XML文件的URL地址")],
    ) -> str:
        """一个查找 XML 内容的工具，返回查找匹配的第一个子元素文本"""
        async with assrf_request("GET", xml_file_url) as resp:
            resp.raise_for_status()
            data = await resp.text()
        root = ET.fromstring(data)
        result = root.find(match)
        if result is None:
            return str(result)
        else:
            return ET.tostring(result, encoding='unicode')

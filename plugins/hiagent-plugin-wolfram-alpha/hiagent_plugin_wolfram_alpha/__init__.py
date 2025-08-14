import os
from pathlib import Path
from typing import Annotated

from langchain_community.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

@set_meta(cn_name="WolframAlpha", en_name="WolframAlpha")
class WolframAlphaPlugin(BasePlugin):
    """Tool that searches the WolframAlpha API."""

    hiagent_tools = ["search"]
    hiagent_category = BuiltinCategory.Education

    def __init__(self, app_id:Annotated[str, SecretField(description="申请地址:<https://developer.wolframalpha.com/access>")]):
        self.app_id = app_id

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def search(self, query: str) -> str:
        return WolframAlphaAPIWrapper(wolfram_alpha_appid=self.app_id).run(query)

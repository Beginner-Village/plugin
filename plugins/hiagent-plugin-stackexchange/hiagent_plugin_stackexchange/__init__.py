import os
from pathlib import Path
# import html
from typing import Annotated
from langchain_community.utilities.stackexchange import StackExchangeAPIWrapper
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory
from pydantic import Field
# import stackexchange

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


@set_meta(cn_name="StackExchange", en_name="StackExchange")
class StackExchangePlugin(BasePlugin):
    """Tool that searches the StackOverflow."""

    hiagent_tools = ["search"]
    hiagent_category = BuiltinCategory.WebSearch
    # def __init__(self,
    #              access_token:Annotated[str, SecretField(description="获取地址:<https://api.stackexchange.com/docs/authentication>")],
    #              key:Annotated[str, SecretField(description="获取地址:<https://api.stackexchange.com/docs/authentication>")],
    #     ):
    #     self.access_token = access_token
    #     self.key = key

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def search(self,
        query: str,
        max_results: Annotated[int, Field(description="返回结果数量")] = 3,
    ) -> str:
        return StackExchangeAPIWrapper(
            # client = StackAPI('stackoverflow',
            #                   **{"key":self.key,
            #                      "access_token": self.access_token}),
            max_results=max_results,
        ).run(query)
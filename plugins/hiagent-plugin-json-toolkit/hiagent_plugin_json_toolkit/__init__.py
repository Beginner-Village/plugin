from typing import Annotated
import os
import json
from pathlib import Path
from pydantic import Field
from hiagent_plugin_sdk import BasePlugin, set_meta, BuiltinCategory, assrf_request
from langchain_community.agent_toolkits import JsonToolkit
from langchain_community.tools.json.tool import JsonSpec

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


@set_meta(cn_name="json工具", en_name="json-toolkit")
class JsonToolkitPlugin(BasePlugin):
    """Toolkit for interacting with a JSON spec."""
    hiagent_tools = ["json_spec_list_keys", "json_spec_get_value"]
    hiagent_category = BuiltinCategory.Productivity

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    async def json_spec_list_keys(self,
        path: Annotated[str, Field(description='representation of the path to the dict in Python syntax (e.g. data["key1"][0]["key2"]')],
        json_file_url: Annotated[str, Field(description="JSON文件的URL地址")],
    ) -> str:
        """Tool for listing keys in a JSON spec.
        Can be used to list all keys at a given path.
        Before calling this you should be SURE that the path to this exists.
        The input is a text representation of the path to the dict in Python syntax (e.g. data["key1"][0]["key2"]).
        """
        async with assrf_request("GET", json_file_url) as resp:
            resp.raise_for_status()
            data = await resp.text()
        data_dict = json.loads(data)
        json_spec = JsonSpec(dict_=data_dict, max_value_length=4000)
        json_toolkit = JsonToolkit(spec=json_spec)
        key_tool, _ = json_toolkit.get_tools()
        return await key_tool.arun(path)

    async def json_spec_get_value(self,
        path: Annotated[str, Field(description='representation of the path to the dict in Python syntax (e.g. data["key1"][0]["key2"]')],
        json_file_url: Annotated[str, Field(description="JSON文件的URL地址")],
    ) -> str:
        """Tool for getting a value in a JSON spec.
        Can be used to see value in string format at a given path.
        Before calling this you should be SURE that the path to this exists.
        The input is a text representation of the path to the dict in Python syntax (e.g. data["key1"][0]["key2"])."""
        async with assrf_request("GET", json_file_url) as resp:
            resp.raise_for_status()
            data = await resp.text()
        data_dict = json.loads(data)
        json_spec = JsonSpec(dict_=data_dict, max_value_length=4000)
        json_toolkit = JsonToolkit(spec=json_spec)
        _, value_tool = json_toolkit.get_tools()
        return await value_tool.arun(path)

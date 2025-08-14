import pytest
import pytest_asyncio
from hiagent_plugin_sdk import BasePlugin, ConfigValidateMixin
from app.sdk.adapter import get_plugin_metadata, run_plugin_validate, run_plugin_tool
from app.config import load
load()

class MyPlugin(BasePlugin):
    """plugin desc"""
    hiagent_tools = ["add"]

    @classmethod
    def _icon_uri(cls) -> str:
        """icon uri"""
        return "file:///path/to/icon.svg"

    def add(self, a: int, b: int) -> int:
        """tool desc"""
        return a+b

    async def aadd(self, a: int, b: int) -> int:
        """tool desc"""
        return a+b

class MyPluginWithConfig(BasePlugin):
    """plugin desc"""
    hiagent_tools = ["add"]

    @classmethod
    def _icon_uri(cls) -> str:
        """icon uri"""
        return "file:///path/to/icon.svg"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def add(self, a: int, b: int) -> int:
        """tool desc"""
        return a+b

class MyPluginWithValidate(BasePlugin, ConfigValidateMixin):
    """plugin desc"""
    hiagent_tools = ["add"]

    def __init__(self, api_key: str):
        self.api_key = api_key

    @classmethod
    def _icon_uri(cls) -> str:
        """icon uri"""
        return "file:///path/to/icon.svg"

    def add(self, a: int, b: int) -> int:
        """tool desc"""
        return a+b

    async def _validate(self) -> None:
        """validate desc"""
        if self.api_key == "":
            raise ValueError("api_key is empty")

@pytest.mark.asyncio
async def test_plugin_metadata():
    meta = get_plugin_metadata(MyPlugin, "my_plugin")
    json_raw = meta.model_dump_json(indent=2)
    print(json_raw)
    assert json_raw == """{
  "name": "my_plugin",
  "class_name": "MyPlugin",
  "labels": {},
  "description": "plugin desc",
  "icon_uri": "file:///path/to/icon.svg",
  "tools": {
    "add": {
      "name": "add",
      "labels": {},
      "description": "tool desc",
      "input_schema": {
        "properties": {
          "a": {
            "title": "A",
            "type": "integer"
          },
          "b": {
            "title": "B",
            "type": "integer"
          }
        },
        "required": [
          "a",
          "b"
        ],
        "title": "InModel",
        "type": "object"
      },
      "output_schema": {
        "title": "OutModel",
        "type": "integer"
      }
    }
  },
  "config_required": false,
  "config_schema": {}
}"""

@pytest.mark.asyncio
async def test_plugin_metadata_config():
    meta = get_plugin_metadata(MyPluginWithConfig, "my_plugin")
    json_raw = meta.model_dump_json(indent=2)
    print(json_raw)
    assert json_raw == """{
  "name": "my_plugin",
  "class_name": "MyPluginWithConfig",
  "labels": {},
  "description": "plugin desc",
  "icon_uri": "file:///path/to/icon.svg",
  "tools": {
    "add": {
      "name": "add",
      "labels": {},
      "description": "tool desc",
      "input_schema": {
        "properties": {
          "a": {
            "title": "A",
            "type": "integer"
          },
          "b": {
            "title": "B",
            "type": "integer"
          }
        },
        "required": [
          "a",
          "b"
        ],
        "title": "InModel",
        "type": "object"
      },
      "output_schema": {
        "title": "OutModel",
        "type": "integer"
      }
    }
  },
  "config_required": true,
  "config_schema": {
    "properties": {
      "api_key": {
        "title": "Api Key",
        "type": "string"
      }
    },
    "required": [
      "api_key"
    ],
    "title": "InModel",
    "type": "object"
  }
}"""


@pytest.mark.asyncio
async def test_plugin_config_validate():
    with pytest.raises(ValueError):
        ins = MyPluginWithValidate(api_key="")
        await run_plugin_validate(ins)
    ins = MyPluginWithValidate(api_key="123")
    ret = await run_plugin_validate(ins)
    assert ret is None

@pytest.mark.asyncio
async def test_plugin_tool():
    with pytest.raises(ValueError):
        ins = MyPluginWithValidate(api_key="")
        await run_plugin_tool(ins, "add2", {"a": 1, "b": 2})

    ins = MyPluginWithValidate(api_key="123")
    ret = await run_plugin_tool(ins, "add", {"a": 1, "b": 2})
    assert ret == 3

import pytest
from urllib.parse import urlparse
from pathlib import Path
from hiagent_plugin_json_toolkit import JsonToolkitPlugin

@pytest.mark.asyncio
async def test_json_spec_list_keys():
    plugin = JsonToolkitPlugin()
    input = {
        "path": 'data["info"]',
        "json_file_url": "http://33.234.129.82:32091/openapi.json"
    }
    result = await plugin.json_spec_list_keys(**input)
    assert result == "['title', 'version']"

@pytest.mark.asyncio
async def test_json_spec_get_value():
    plugin = JsonToolkitPlugin()
    input = {
        "path": 'data["info"]["version"]',
        "json_file_url": "http://33.234.129.82:32091/openapi.json"
    }
    result = await plugin.json_spec_get_value(**input)
    assert result == "0.1.0"

def test_icon_uri():
    plugin = JsonToolkitPlugin()
    uri = plugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

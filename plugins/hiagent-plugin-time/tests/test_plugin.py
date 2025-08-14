import pytest
from urllib.parse import urlparse
from pathlib import Path
from hiagent_plugin_time import TimePlugin


@pytest.mark.asyncio
async def test_current_time():
    plugin = TimePlugin()
    result = await plugin.current_time(**{"timezone": "asia/shanghai"})
    assert result != ""

def test_icon_uri():
    plugin = TimePlugin()
    uri = plugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

import os
import pytest
from urllib.parse import urlparse
from pathlib import Path
from hiagent_plugin_regex import RegexPlugin


def test_icon_uri():
    plugin = RegexPlugin()
    uri = plugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_parse():
    ins = RegexPlugin()
    req = {
        "content": "1+(2+3)*4",
        "expression": r"(\d+)",
    }
    ret = await ins.regex_extract(**req)
    print(ret)
    assert ret == ['1', '2', '3', '4']

import pytest
import os
import json
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_taopiaopiao import TaopiaopiaoPlugin
from dotenv import load_dotenv
load_dotenv("../../.env")

def test_icon_uri():
    uri = TaopiaopiaoPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_GetMovieAndShow():
    cfg = os.getenv("TAOPIAOPIAO_CONFIG")
    cfg_dict = json.loads(cfg)
    plugin = TaopiaopiaoPlugin(**cfg_dict)
    data = await plugin.GetMovieAndShow(**{
        "page_index": 1,
        "page_size": 5,
    })
    print(data)
    assert len(data.return_value.show) > 0

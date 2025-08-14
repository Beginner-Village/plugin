import os
import pytest
from pathlib import Path
import json
from urllib.parse import urlparse
from hiagent_plugin_volc_searchbot import VolcSearchBot
from dotenv import load_dotenv
load_dotenv("../../.env")

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_SmartSearch():
    cfg = os.getenv("VOLC_SEARCHBOT_CONFIG")
    # cfg = os.getenv("VOLC_SEARCHBOT_CONFIG_FAILED")
    cfg_dict = json.loads(cfg)
    ins = VolcSearchBot(**cfg_dict)
    ret = await ins.SmartSearch(**{"query": "今日中国要闻"})
    print(ret)
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_SmartSearchStream():
    # cfg = os.getenv("VOLC_SEARCHBOT_CONFIG")
    cfg = os.getenv("VOLC_SEARCHBOT_CONFIG_FAILED")
    cfg_dict = json.loads(cfg)
    ins = VolcSearchBot(**cfg_dict)
    async for ret in ins.SmartSearch_stream(**{"query": "今日中国要闻"}):
        print(ret)
    assert False

def test_icon_uri():
    uri = VolcSearchBot._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

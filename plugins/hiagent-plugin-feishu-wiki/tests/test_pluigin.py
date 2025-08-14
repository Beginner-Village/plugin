import os
import pytest
import json
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_feishu_wiki import FeishuWikiPlugin
from dotenv import load_dotenv
load_dotenv("../../.env")


def test_icon_uri():
    uri = FeishuWikiPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_get_wiki_nodes():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuWikiPlugin(**cfg_dict)
    req = {
        "space_id": "7446288580011540484",
    }
    ret = await ins.get_wiki_nodes(**req)
    print(ret)
    assert len(ret.data.items) > 0

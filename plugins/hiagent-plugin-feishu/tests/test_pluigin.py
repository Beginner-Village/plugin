import os
import pytest
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_feishu import FeishuPlugin
from dotenv import load_dotenv
load_dotenv("../../.env")

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_feishu_group_bot():
    hook_key = os.getenv("FEISHU_HOOK_KEY")
    ins = FeishuPlugin(**{"hook_key": hook_key, "host": ""})
    ret = await ins.feishu_group_bot(**{"content": "test"})
    assert ret == "Success"

def test_icon_uri():
    uri = FeishuPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

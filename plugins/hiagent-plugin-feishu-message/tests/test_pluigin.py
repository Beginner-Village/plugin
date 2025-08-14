import os
import pytest
import json
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_feishu_message import FeishuMessagePlugin
from dotenv import load_dotenv
load_dotenv("../../.env")


def test_icon_uri():
    uri = FeishuMessagePlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_send_message():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuMessagePlugin(**cfg_dict)
    req = {
        "receive_id_type": "chat_id",
        "receive_id": "oc_f82d13920641908dfeaafe39ebbb5988",
        "msg_type": "text",
        "content": "{\"text\":\"test content\"}",
    }
    ret = await ins.send_message(**req)
    print(ret)
    assert len(ret.data.items) > 0

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_list_chat():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuMessagePlugin(**cfg_dict)
    req = {
        "user_id_type": "open_id",
    }
    ret = await ins.list_chat(**req)
    print(ret)
    assert ret.data.body is not None
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_list_message():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuMessagePlugin(**cfg_dict)
    req = {
        "container_id_type": "chat",
        "container_id": "oc_f82d13920641908dfeaafe39ebbb5988",
        "start_time": "1608594809",
        # "end_time": "1908594809",
    }
    ret = await ins.list_message(**req)
    print(ret)
    assert len(ret.data.items) > 0
    assert False

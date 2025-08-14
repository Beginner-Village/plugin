import os
import pytest
import json
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_feishu_task import FeishuTaskPlugin
from dotenv import load_dotenv
load_dotenv("../../.env")


def test_icon_uri():
    uri = FeishuTaskPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_create_task():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuTaskPlugin(**cfg_dict)
    req = {
        "input_task": {
            "summary": "1209_1806"
        }
    }
    ret = await ins.create_task(**req)
    print(ret)
    assert ret.data.task is not None
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_update_task():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuTaskPlugin(**cfg_dict)
    req = {
        "task_guid": "f3dec02a-54c0-45b9-832e-2fbc7f3b8b5f",
        "update_fields": ["summary"],
        "input_task": {
            "summary": "1209_1854"
        }
    }
    ret = await ins.update_task(**req)
    print(ret)
    assert ret.data.task is not None
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_delete_task():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuTaskPlugin(**cfg_dict)
    req = {
        "task_guid": "ca9920d8-ebf1-43dc-9de8-4a75e4a3b2c4",
    }
    ret = await ins.delete_task(**req)
    print(ret)
    assert ret.data.code == 0

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_add_members():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuTaskPlugin(**cfg_dict)
    req = {
        "task_guid": "42825103-5594-4d0a-86d6-fcec37e3b338",
        "members": [{
            "id": "cli_a7dbcaadff27d013",
            "type": "app",
            "role": "assignee",
        }],
    }
    ret = await ins.add_members(**req)
    print(ret)
    assert ret.data.task is not None

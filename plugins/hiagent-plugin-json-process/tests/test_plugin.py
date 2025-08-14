import os
import json
import pytest
from urllib.parse import urlparse
from pathlib import Path
from hiagent_plugin_json_process import JsonProcessPlugin


def test_icon_uri():
    plugin = JsonProcessPlugin()
    uri = plugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_parse():
    ins = JsonProcessPlugin()
    req = {
        "content": '{"name": "json"}',
        "json_filter": "$.name",
    }
    ret = await ins.parse(**req)
    print(ret)
    assert ret == "json"
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_insert():
    ins = JsonProcessPlugin()
    req = {
        "content": '{"name": "json"}',
        "query": "$.name2",
        "new_value": "yaml",
        "create_path": True
    }
    ret = await ins.insert(**req)
    print(ret)
    assert ret == '{"name": "json", "name2": "yaml"}'
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_delete():
    ins = JsonProcessPlugin()
    req = {
        "content": '{"name": "json", "age": 18}',
        "query": "$.name",
    }
    ret = await ins.delete(**req)
    print(ret)
    assert ret == '{"age": 18}'
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_replace():
    ins = JsonProcessPlugin()
    req = {
        "content": '{"name": "json", "age": 18}',
        "query": "$.name",
        "replace_value": '{"k": "v"}',
        "value_decode": True,
    }
    ret = await ins.replace(**req)
    print(ret)
    assert ret == '{"name": {"k": "v"}, "age": 18}'
    assert False

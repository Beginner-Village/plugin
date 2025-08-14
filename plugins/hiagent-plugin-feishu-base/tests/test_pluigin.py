import os
import pytest
import json
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_feishu_base import FeishuBasePlugin
from dotenv import load_dotenv
load_dotenv("../../.env")


def test_icon_uri():
    uri = FeishuBasePlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_create_base():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuBasePlugin(**cfg_dict)
    req = {
        "name": "1206_1639",
        "folder_token": "Fq19fKrcwlhcb6dLcrcceXUanoc",
    }
    ret = await ins.create_base(**req)
    print(ret)
    assert False


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_get_base_info():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuBasePlugin(**cfg_dict)
    req = {
        "app_token": "BhtUbKNOyalO2ysT5pac3I48nAg",
    }
    ret = await ins.get_base_info(**req)
    print(ret)
    assert False


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_create_table():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuBasePlugin(**cfg_dict)
    req = {
        "app_token": "Qia1bQg6IagcN5sPbvAc7yUgnGf",
        "name": "table_2",
        # "fields": [{"field_name": "索引字段","type": 1}],
    }
    ret = await ins.create_table(**req)
    print(ret)
    assert False


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_list_table():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuBasePlugin(**cfg_dict)
    req = {
        "app_token": "BhtUbKNOyalO2ysT5pac3I48nAg",
        "page_size": 2,
    }
    ret = await ins.list_table(**req)
    print(ret)
    assert False


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_delete_table():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuBasePlugin(**cfg_dict)
    req = {
        "app_token": "BhtUbKNOyalO2ysT5pac3I48nAg",
        "table_id": "tblNItgb9352kegi",
    }
    ret = await ins.delete_table(**req)
    print(ret)
    assert False


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_create_records():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuBasePlugin(**cfg_dict)
    req = {
        "app_token": "BhtUbKNOyalO2ysT5pac3I48nAg",
        "table_id": "tblmzQHL2SPMfDe9",
        # "fields": {
        #     "索引字段": "拜访潜在客户",
        # }
        "fields_json": "{\"col1\": 1, \"col2\": \"a\" }",
    }
    ret = await ins.create_records(**req)
    print(ret)
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_update_records():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuBasePlugin(**cfg_dict)
    req = {
        "app_token": "BhtUbKNOyalO2ysT5pac3I48nAg",
        "table_id": "tblmzQHL2SPMfDe9",
        "record_id": "recuwa7e1e3rdU",
        "fields": {
            "索引字段": "拜访潜在客户2",
        }
    }
    ret = await ins.update_records(**req)
    print(ret)
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_search_records():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuBasePlugin(**cfg_dict)
    req = {
        "app_token": "BhtUbKNOyalO2ysT5pac3I48nAg",
        "table_id": "tblmzQHL2SPMfDe9",
        "page_size": 2,
        "search": {
            "field_names": ["索引字段"],
        }
    }
    ret = await ins.search_records(**req)
    print(ret)
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_delete_records():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuBasePlugin(**cfg_dict)
    req = {
        "app_token": "BhtUbKNOyalO2ysT5pac3I48nAg",
        "table_id": "tblmzQHL2SPMfDe9",
        "record_id": "recuwa7e1e3rdU",
    }
    ret = await ins.delete_records(**req)
    print(ret)
    assert False

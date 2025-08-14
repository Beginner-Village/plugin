import os
import pytest
import json
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_feishu_spreadsheet import FeishuSpreadSheetPlugin
from dotenv import load_dotenv
load_dotenv("../../.env")


def test_icon_uri():
    uri = FeishuSpreadSheetPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_create_spreadsheet():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuSpreadSheetPlugin(**cfg_dict)
    req = {
        "folder_token": "Fq19fKrcwlhcb6dLcrcceXUanoc",
        "title": "1209_1440"
    }
    ret = await ins.create_spreadsheet(**req)
    print(ret)
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_get_spreadsheet():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuSpreadSheetPlugin(**cfg_dict)
    req = {
        "spreadsheet_token": "Jx0hspAINhI9xstYuGtcUPLlnZf",
    }
    ret = await ins.get_spreadsheet(**req)
    print(ret)
    assert ret.data.spreadsheet.token != ""

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_list_sheets():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuSpreadSheetPlugin(**cfg_dict)
    req = {
        "spreadsheet_token": "Jx0hspAINhI9xstYuGtcUPLlnZf",
    }
    ret = await ins.list_sheets(**req)
    print(ret)
    assert len(ret.data.sheets) > 0

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_get_sheet():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuSpreadSheetPlugin(**cfg_dict)
    req = {
        "spreadsheet_token": "Jx0hspAINhI9xstYuGtcUPLlnZf",
        "sheet_id": "dd4dd5",
    }
    ret = await ins.get_sheet(**req)
    print(ret)
    assert ret.data.sheet is not None

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_add_rows_or_columns():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuSpreadSheetPlugin(**cfg_dict)
    req = {
        "spreadsheet_token": "Jx0hspAINhI9xstYuGtcUPLlnZf",
        "dimension": {"sheetId": "dd4dd5","majorDimension": "ROWS","length": 1},
    }
    ret = await ins.add_rows_or_columns(**req)
    print(ret)
    assert ret.data.addCount > 0

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_read_range():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuSpreadSheetPlugin(**cfg_dict)
    req = {
        "spreadsheet_token": "Jx0hspAINhI9xstYuGtcUPLlnZf",
        "range": "dd4dd5!A1:B2",
    }
    ret = await ins.read_range(**req)
    print(ret)
    assert len(ret.data.valueRange.rowValues) > 0

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_write_range():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuSpreadSheetPlugin(**cfg_dict)
    req = {
        "spreadsheet_token": "Jx0hspAINhI9xstYuGtcUPLlnZf",
        "values": {"range": "dd4dd5!A1:B2","rowValues": [{"values": ["A1", "B1"]},{"values": ["b", "2"]}]},
    }
    ret = await ins.write_range(**req)
    print(ret)
    # assert ret.data.updatedRows > 0
    assert False

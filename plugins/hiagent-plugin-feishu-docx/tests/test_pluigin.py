import os
import pytest
import json
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_feishu_docx import FeishuDocxPlugin
from dotenv import load_dotenv
load_dotenv("../../.env")


def test_icon_uri():
    uri = FeishuDocxPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_create_document():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuDocxPlugin(**cfg_dict)
    req = {
        "folder_token": "Fq19fKrcwlhcb6dLcrcceXUanoc",
        "title": "1210_1047"
    }
    ret = await ins.create_document(**req)
    print(ret)
    assert ret.data.document is not None
    assert False


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_get_document():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuDocxPlugin(**cfg_dict)
    req = {
        "document_id": "OULzdJtv2omvX9xS7Jocjy37nBU",
    }
    ret = await ins.get_document(**req)
    print(ret)
    assert ret.data.document is not None
    assert False


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_get_document_content():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuDocxPlugin(**cfg_dict)
    req = {
        "document_id": "OULzdJtv2omvX9xS7Jocjy37nBU",
    }
    ret = await ins.get_document_content(**req)
    print(ret)
    assert ret.data.content != ""
    assert False


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_list_document_block():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuDocxPlugin(**cfg_dict)
    req = {
        "document_id": "OULzdJtv2omvX9xS7Jocjy37nBU",
    }
    ret = await ins.list_document_block(**req)
    print(ret)
    assert len(ret.data.items) > 0
    assert False


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_create_document_block():
    cfg = os.getenv("FEISHU_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = FeishuDocxPlugin(**cfg_dict)
    req = {
        "document_id": "OULzdJtv2omvX9xS7Jocjy37nBU",
        "block_id": "GcQjdhex5oEVy0x9hRJclBgEnId",
        "content": {
            "children": [{
                "block_type": 2,
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "多人实时协同，插入一切元素。不仅是在线文档，更是",
                                "text_element_style": {
                                    "background_color": 14,
                                    "text_color": 5
                                }
                            }
                        },
                        {
                            "text_run": {
                                "content": "强大的创作和互动工具",
                                "text_element_style": {
                                    "background_color": 14,
                                    "bold": True,
                                    "text_color": 5
                                }
                            }
                        }
                    ],
                    "style": {}
                }
            }],
            "index": 0,
        },
    }
    ret = await ins.create_document_block(**req)
    print(ret)
    assert len(ret.data.children) > 0
    assert False

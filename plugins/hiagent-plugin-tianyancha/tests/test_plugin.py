import pytest
import os
from urllib.parse import urlparse
from pathlib import Path
from hiagent_plugin_tianyancha import TianyanchaPlugin
from dotenv import load_dotenv
load_dotenv("../../.env")


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_abnormal_operation():
    token = os.getenv("TIANYANCHA_TOKEN")
    plugin = TianyanchaPlugin(token)
    result = await plugin.abnormal_operation(**{"keyword": "宁夏凯捷建设工程有限公司"})
    print(result)
    assert len(result.items) > 0


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_news():
    token = os.getenv("TIANYANCHA_TOKEN")
    plugin = TianyanchaPlugin(token)
    result = await plugin.news(**{"name": "北京抖音信息服务有限公司"})
    print(result)
    assert len(result.items) > 0
    assert False


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_company_detail():
    token = os.getenv("TIANYANCHA_TOKEN")
    plugin = TianyanchaPlugin(token)
    result = await plugin.company_detail(**{"keyword": "北京抖音信息服务有限公司"})
    print(result)
    assert result.fromTime != ""


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_change_log():
    token = os.getenv("TIANYANCHA_TOKEN")
    plugin = TianyanchaPlugin(token)
    result = await plugin.change_log(**{"keyword": "北京抖音信息服务有限公司"})
    print(result)
    assert len(result.items) > 0


def test_icon_uri():
    uri = TianyanchaPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

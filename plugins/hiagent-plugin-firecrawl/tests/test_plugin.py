import os
import pytest
from urllib.parse import urlparse
from pathlib import Path
from hiagent_plugin_firecrawl import FirecrawlPlugin


def get_firecrawl_plugin():
    return FirecrawlPlugin(
        api_key="xxx",
    )

def test_icon_uri():
    plugin = get_firecrawl_plugin()
    uri = plugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_crawl():
    ins = get_firecrawl_plugin()
    ret = await ins.crawl(url="https://www.baidu.com")
    print(ret)
    assert ret

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_crawl_job():
    ins = get_firecrawl_plugin()
    ret = await ins.crawl_job(job_id="4b23bdd2-8bd4-478d-87df-88c7d031dd18", operation="get")
    print(ret)
    assert ret
    ret = await ins.crawl_job(job_id="4b23bdd2-8bd4-478d-87df-88c7d031dd18", operation="cancel")
    print(ret)
    assert ret

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_scrape():
    ins = get_firecrawl_plugin()
    ret = await ins.scrape(url="https://www.baidu.com")
    print(ret)
    assert ret

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_map():
    ins = get_firecrawl_plugin()
    ret = await ins.map(url="https://www.baidu.com", search="baidu")
    print(ret)
    assert ret

import pytest
import os
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_webscraper import WebscraperPlugin
from dotenv import load_dotenv
load_dotenv("../../.env")


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_get_url_html():
    plugin = WebscraperPlugin()
    arg = {"url": "https://www.volcengine.com/"}
    result = plugin.get_url(**arg)
    print(result)
    assert result != ""

@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_get_url_pdf():
    plugin = WebscraperPlugin()
    arg = {"url": "https://arxiv.org/pdf/1706.03762"}
    result = plugin.get_url(**arg)
    print(result)
    assert result != ""


def test_icon_uri():
    uri = WebscraperPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

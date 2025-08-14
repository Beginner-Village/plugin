import os
import pytest
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_bingsearch import BingSearchPlugin
from dotenv import load_dotenv
load_dotenv("../../.env")

@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_search():
    api_key = os.getenv("BING_SEARCH_API_KEY")
    ins = BingSearchPlugin(**{"api_key": api_key})
    ret = ins.search(**{"query": "test"})
    assert ret != ""


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_search_result():
    api_key = os.getenv("BING_SEARCH_API_KEY")
    ins = BingSearchPlugin(**{"api_key": api_key})
    ret = ins.search_results(**{"query": "test", "num_results": 1})
    assert len(ret) > 0

def test_icon_uri():
    uri = BingSearchPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

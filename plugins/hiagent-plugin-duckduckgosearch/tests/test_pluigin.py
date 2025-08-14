import os
import pytest
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_duckduckgosearch import DuckDuckGoSearchPlugin
from dotenv import load_dotenv
load_dotenv("../../.env")


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_search():
    ins = DuckDuckGoSearchPlugin()
    ret = ins.search(**{"query": "test"})
    assert ret != ""


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_search_result():
    ins = DuckDuckGoSearchPlugin()
    ret = ins.search_results(**{"query": "Obama", "max_results": 1})
    print(ret)
    assert len(ret) > 0

def test_icon_uri():
    uri = DuckDuckGoSearchPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()
import pytest
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from pathlib import Path
from hiagent_plugin_wikipedia import WikipediaPlugin
load_dotenv("../../.env")

@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_search():
    plugin = WikipediaPlugin()
    result = plugin.search(**{"query": "LLM", "lang": "en"})
    print(result)
    assert result != ""


def test_icon_uri():
    uri = WikipediaPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

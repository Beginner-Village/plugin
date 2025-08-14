import pytest
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from pathlib import Path
from hiagent_plugin_wikidata import WikidataPlugin
load_dotenv("../../.env")

def test_icon_uri():
    uri = WikidataPlugin._icon_uri()
    # print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_search():
    plugin = WikidataPlugin()
    req = {
        "query": "Alan Turing",
    }
    result = plugin.search(**req)
    print(result)
    assert result != ""

# @pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
# def test_search_doc():
#     plugin = WikidataPlugin()
#     req = {
#         "query": "Alan Turing",
#     }
#     result = plugin.search_doc(**req)
#     print(result)
#     assert len(result) > 0
#     assert False

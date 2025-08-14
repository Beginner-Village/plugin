import pytest
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from pathlib import Path
from hiagent_plugin_wolfram_alpha import WolframAlphaPlugin
load_dotenv("../../.env")

# @pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
# def test_search():
#     plugin = WolframAlphaPlugin(app_id="")
#     result = plugin.search(**{"query": "What is 2x + 5 = -3x + 7?"})
#     print(result)
#     assert result != ""


def test_icon_uri():
    uri = WolframAlphaPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

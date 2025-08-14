import os
import pytest
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_yahoo_finance import YahooPlugin
from dotenv import load_dotenv

load_dotenv("../../.env")


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_search():
    print("test_search")
    ins = YahooPlugin()

    symbol = "AAPL"
    start_date = "2020-01-01"
    end_date = "2023-12-31"

    # result = ins.analytics(symbol, start_date, end_date)
    # print(result)
    # assert result != ""

    # result = ins.news(symbol)
    # print(result)
    # assert result != ""
    #
    result = ins.ticker(symbol)
    print(result)
    assert result != ""


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_icon_uri():
    uri = YahooPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

import pytest
import os
import json
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_mojiweather import MojiWeatherPlugin
from dotenv import load_dotenv
load_dotenv("../../.env")

def test_icon_uri():
    uri = MojiWeatherPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_CurrentWeather():
    cfg = os.getenv("MOJIWEATHER_CONFIG")
    cfg_dict = json.loads(cfg)
    plugin = MojiWeatherPlugin(**cfg_dict)
    data = await plugin.CurrentWeather(**{
        "name": "西湖区",
        "parent": "美国",
    })
    print(data)
    assert data.msg == "success"
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_Latest40DayWeather():
    cfg = os.getenv("MOJIWEATHER_CONFIG")
    cfg_dict = json.loads(cfg)
    plugin = MojiWeatherPlugin(**cfg_dict)
    data = await plugin.Latest40DayWeather(**{
        "city": "杭州市",
    })
    print(data)
    assert len(data.data.daily) > 0

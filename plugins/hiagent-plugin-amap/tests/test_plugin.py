import pytest
import os
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_amap import AmapPlugin
from dotenv import load_dotenv
load_dotenv("../../.env")

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_poi_to_geocode():
    token = os.getenv("AMAP_API_KEY")
    plugin = AmapPlugin(token)
    result = await plugin.poi_to_geocode(**{"address": "杭州八方城"})
    print(result)
    assert len(result.geocodes) > 0

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_plan_walking():
    token = os.getenv("AMAP_API_KEY")
    plugin = AmapPlugin(token)
    result = await plugin.plan_walking(**{"start": "116.481028,39.989643", "destination": "116.434446,39.90816"})
    print(result)
    assert len(result.route.paths) > 0

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_plan_driving():
    token = os.getenv("AMAP_API_KEY")
    plugin = AmapPlugin(token)
    result = await plugin.plan_driving(**{"start": "116.481028,39.989643", "destination": "116.434446,39.90816"})
    print(result)
    assert len(result.route.paths) > 0

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_plan_integrated():
    token = os.getenv("AMAP_API_KEY")
    plugin = AmapPlugin(token)
    result = await plugin.plan_integrated(**{"start": "116.481028,39.989643", "destination": "116.434446,39.90816", "city": "北京"})
    print(result)
    assert len(result.route.transits) > 0

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_plan_bicycle():
    token = os.getenv("AMAP_API_KEY")
    plugin = AmapPlugin(token)
    result = await plugin.plan_bicycle(**{"start": "116.481028,39.989643", "destination": "116.434446,39.90816"})
    print(result)
    assert len(result.data.paths) > 0

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_validate():
    token = os.getenv("AMAP_API_KEY")
    plugin = AmapPlugin(token)
    await plugin._validate()

def test_icon_uri():
    uri = AmapPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

# def test_jsonschema():
#     from hiagent_plugin_amap.plan_walking import PlanWalkingResult
#     import json
#     dst = PlanWalkingResult.model_json_schema(mode='serialization')
#     print(json.dumps(dst, indent=2))
#     assert False

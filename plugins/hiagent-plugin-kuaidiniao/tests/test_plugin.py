import pytest
import os
from urllib.parse import urlparse
from pathlib import Path
import json
from hiagent_plugin_kuaidiniao import KuaidiniaoPlugin
from dotenv import load_dotenv
load_dotenv("../../.env")

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_ExpressDelivery():
    cfg = os.getenv("KUAIDINIAO_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = KuaidiniaoPlugin(**cfg_dict)
    result = await ins.ExpressDelivery(**{"LogisticCode": "JT3095828741092"})
    print(result)
    assert len(result.Traces) > 0

# def test_sign():
#     req_data = {
#         "OrderCode": "",
#         "CustomerName": "5195",
#         "ShipperCode": "SF",
#         "LogisticCode": "SF1613099010320"
#     }
#     api_key = "56da2cf8-c8a2-44b2-b6fa-476cd7d1ba17"
#     import json
#     sign_data = f"{json.dumps(req_data, separators=(',', ': '))}{api_key}"
#     s1 = sign_data
#     print("sign_data: ", s1)
#     # {"OrderCode": "", "CustomerName": "5195", "ShipperCode": "SF", "LogisticCode": "SF1613099010320"}56da2cf8-c8a2-44b2-b6fa-476cd7d1ba17
#     # {"OrderCode": "","CustomerName": "5195","ShipperCode": "SF","LogisticCode": "SF1613099010320"}56da2cf8-c8a2-44b2-b6fa-476cd7d1ba17
#     import hashlib
#     s2 = hashlib.md5(sign_data.encode()).hexdigest()
#     print("s2: ", s2)
#     import base64
#     s3 = base64.b64encode(s2.encode()).decode()
#     print("s3: ", s3)
#     from urllib.parse import quote
#     s4 = quote(s3)
#     print("s4: ", s4)
#     assert s3 == "MTYzYTMwMzlhZGIzZjIwNGM3OGYzZmI2ZmVjY2IwZmE%3D"

def test_icon_uri():
    uri = KuaidiniaoPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

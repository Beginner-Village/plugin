import os
import pytest
from pathlib import Path
import json
from urllib.parse import urlparse
from hiagent_plugin_volc_text2image import VolcText2Image
from dotenv import load_dotenv
load_dotenv("../../.env")

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_text2image():
    cfg = os.getenv("VOLC_TEXT2IMAGE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = VolcText2Image(**cfg_dict)
    ret = await ins.text2image(**{"prompt": "加班的程序员"})
    print(ret)
    assert ret.image_url != ""
    assert ret.pe_result != ""
    assert False

def test_icon_uri():
    uri = VolcText2Image._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

@pytest.mark.skipif(True)
def test_image_decode():
    with open("./tests/resp.json", "r", encoding="utf-8") as f:
        data_dict = json.load(f)
    from hiagent_plugin_volc_text2image import VolcResp
    data = VolcResp(**data_dict)
    import base64
    image = base64.standard_b64decode(data.data.binary_data_base64[0])
    with open("./tests/image.png", "wb") as f:
        f.write(image)

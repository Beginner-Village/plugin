import os
import pytest
from pathlib import Path
import json
from urllib.parse import urlparse
from hiagent_plugin_volc_speech2textllm import VolcSpeech2Text
from dotenv import load_dotenv
load_dotenv("../../.env")

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_SpeechToText():
    cfg = os.getenv("VOLC_SPEECH2TEXTLLM_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = VolcSpeech2Text(**cfg_dict)
    req = {
        # "url": "https://torch-hk-public-jack.tos-cn-hongkong.bytepluses.com/SetSail/(17%20to%2031%20July%202024)_(Cantonese)_(Part1)%20(1).wav",
        "url": "https://p6-bot-sign.byteimg.com/tos-cn-i-v4nquku3lp/45c0fba3363049f6bbfb3f5f55930672.wav~tplv-v4nquku3lp-image.image?rk3s=68e6b6b5&x-expires=1741351483&x-signature=mLEv5CqrntRIv5fp4x7gmEspspk%3D",
        "format": "wav",
        "enable_speaker_info": True,
    }
    ret = await ins.SpeechToText(**req)
    print(f"ret: {ret}")
    assert ret != ""
    assert False

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_query():
    cfg = os.getenv("VOLC_SPEECH2TEXTLLM_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = VolcSpeech2Text(**cfg_dict)
    ok, ret = await ins._query("138b80d0-ff03-4ff6-b5f4-1f1f87481c98")
    print(f"{ok}, ret: {ret}")
    assert ret != ""
    assert False


def test_icon_uri():
    uri = VolcSpeech2Text._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

import os
import pytest
from pathlib import Path
import json
from urllib.parse import urlparse
from hiagent_plugin_volc_speech2text import VolcSpeech2Text
from dotenv import load_dotenv
load_dotenv("../../.env")

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_SpeechToText():
    cfg = os.getenv("VOLC_SPEECH2TEXT_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = VolcSpeech2Text(**cfg_dict)
    # ret = await ins.SpeechToText(**{"url": "http://33.234.129.82:32300/api/proxy/down?Action=Download&Version=2022-01-01&Path=upload%2Ffull%2Fcf%2F42%2F612fdd4795337fb0acbc2720cc6a818497ffdaf2db1d7500a06613eaa60a&IsAnonymous=true", "format": "mp3"})
    # ret = await ins.SpeechToText(**{"url": "file:///Users/bytedance/Desktop/nlp_test/nlp_test.mp3", "format": "mp3"})
    # ret = await ins.SpeechToText(**{"url": "file:///Users/bytedance/Desktop/nlp_test/nlp_test.wav", "format": "wav"})
    # ret = await ins.SpeechToText(**{"url": "file:///Users/bytedance/Desktop/nlp_test/nlp_test.ogg", "format": "ogg"})
    # ret = await ins.SpeechToText(**{"url": "http://14.103.44.217:3000/api/proxy/down?Action=Download&Version=2022-01-01&Path=upload%2Ffull%2Fec%2F80%2Ff3d3f0231d6c9582fb70687e93e7a239071839d56844e238007a828abc24&IsAnonymous=true", "format": "ogg"})
    # ret = await ins.SpeechToText(**{"url": "file:///Users/bytedance/Desktop/code.byted.org/plugin-runtime/.vscode/test.ogg", "format": "ogg"})
    # ret = await ins.SpeechToText(**{"url": "file:///Users/bytedance/Desktop/code.byted.org/plugin-runtime/.vscode/test2.ogg", "format": "ogg"})
    # ret = await ins.SpeechToText(**{"url": "file:///Users/bytedance/Desktop/code.byted.org/plugin-runtime/.vscode/nlp_test2.ogg", "format": "ogg"})
    # ret = await ins.SpeechToText(**{"url": "file:///Users/bytedance/Desktop/连丽如-红楼梦001-2.mp3", "format": "mp3"})
    # ret = await ins.SpeechToText(**{"url": "file:///Users/bytedance/Downloads/(17 to 31 July 2024)_(Cantonese)_(Part1) (1).wav", "format": "wav"})
    ret = await ins.SpeechToText(**{"url": "https://torch-hk-public-jack.tos-cn-hongkong.bytepluses.com/SetSail/(17%20to%2031%20July%202024)_(Cantonese)_(Part1)%20(1).wav", "format": "wav"})
    print(f"ret: {ret}")
    assert ret != ""
    assert False

def test_icon_uri():
    uri = VolcSpeech2Text._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_aiofile():
    import aiofiles as aiof
    import aiohttp
    url = "http://33.234.129.82:32300/api/proxy/down?Action=Download&Version=2022-01-01&Path=upload%2Ffull%2Fcf%2F42%2F612fdd4795337fb0acbc2720cc6a818497ffdaf2db1d7500a06613eaa60a&IsAnonymous=true"
    async with aiof.tempfile.NamedTemporaryFile() as f:
        async with aiohttp.request("GET", url) as resp:
            resp.raise_for_status()
            async for trunc in resp.content.iter_chunked(8192):
                print(f"trunc: {len(trunc)}")
                await f.write(trunc)
            await f.flush()
        data = await f.read()
        print(f"filename: {f.name}")
        async with aiof.open(f.name, "rb") as f2:
            data = await f2.read()
            print(f"data: {len(data)}")
            assert len(data) > 0

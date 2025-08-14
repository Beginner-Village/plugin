import os
import pytest
from urllib.parse import urlparse
from pathlib import Path
from hiagent_plugin_vectorizer_ai import VectorizerAIPlugin


def test_icon_uri():
    plugin = VectorizerAIPlugin()
    uri = plugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_vectorize():
    ins = VectorizerAIPlugin(
        api_key_name="xxx",
        api_key_value="yyy"
    )
    ret = await ins.vectorize(image_url="https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png")
    print(ret)
    assert ret

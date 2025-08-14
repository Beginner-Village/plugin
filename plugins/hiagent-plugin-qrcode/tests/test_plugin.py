import os
import json
import pytest
from urllib.parse import urlparse
from pathlib import Path
from hiagent_plugin_qrcode import QRCodePlugin


def test_icon_uri():
    plugin = QRCodePlugin()
    uri = plugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_qrcode_generator():
    ins = QRCodePlugin()
    req = {
        "content": 'https://www.volcengine.com',
    }
    ret = ins.qrcode_generator(**req)
    print(ret)
    assert ret != ""
    assert False

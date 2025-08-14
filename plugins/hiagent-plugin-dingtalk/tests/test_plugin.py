import os
import pytest
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_dingtalk import DingTalkPlugin
from dotenv import load_dotenv

load_dotenv("../../.env")


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_search():
    print("test_search")
    ins = DingTalkPlugin()

    content = "ceshi"
    access_token = os.getenv("ACCESS_TOKEN"),
    sign_secret = os.getenv("SIGN_SECRET")

    result = ins.ding_robot_send(content, access_token, sign_secret)
    print(result)
    assert result != ""


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_icon_uri():
    uri = DingTalkPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

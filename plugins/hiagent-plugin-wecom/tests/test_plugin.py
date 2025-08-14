import os
import pytest
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_wecom import WecomPlugin
from dotenv import load_dotenv

load_dotenv("../../.env")


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_search():
    print("test_search")
    ins = WecomPlugin()

    content = "集帅们，你们好"
    hook_key = os.getenv("HOOK_KEY")
    message_type = os.getenv("MESSAGE_TYPE")

    result = ins.wecom_robot_send(content, hook_key, message_type)
    print(result)
    assert result != ""


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_icon_uri():
    uri = WecomPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

import os
import pytest
import json
from hiagent_plugin_notiontoolspec import NotionToolSpecPlugin
from dotenv import load_dotenv

load_dotenv("../../../.env")


# @pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_search_data():
    ret = NotionToolSpecPlugin(os.getenv("NOTION_INTEGRATION_TOKEN")).search_data("page")
    print(ret)
    assert ret != ""


def test_load_data():
    ret = NotionToolSpecPlugin(os.getenv("NOTION_INTEGRATION_TOKEN")).load_data("15f502a6dd6b80c688e0cc466c065ad5")
    print(ret)
    assert ret != ""

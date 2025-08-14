import os
import pytest
from urllib.parse import urlparse
from pathlib import Path
from hiagent_plugin_xml_toolkit import XmlToolkitPlugin


def test_icon_uri():
    plugin = XmlToolkitPlugin()
    uri = plugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
async def test_xml_spec_find_element():
    plugin = XmlToolkitPlugin()
    input = {
        "match": 'body',
        "xml_file_url": "https://www.w3schools.com/xml/note.xml"
    }
    result = await plugin.xml_spec_find_element(**input)
    print(result)
    assert result == "<body>Don't forget me this weekend!</body>"
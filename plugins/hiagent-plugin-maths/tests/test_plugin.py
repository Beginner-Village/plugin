import pytest
from urllib.parse import urlparse
from pathlib import Path
from hiagent_plugin_maths import MathsPlugin


def test_eval_expression():
    plugin = MathsPlugin()
    result = plugin.eval_expression("1+1")
    assert result == "2"

def test_icon_uri():
    uri = MathsPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()

import os
import pytest
import json
from pathlib import Path
from urllib.parse import urlparse
from hiagent_plugin_salesforce import SalesforcePlugin
from dotenv import load_dotenv

load_dotenv("../../.env")


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_icon_uri():
    uri = SalesforcePlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_execute_sosl():
    cfg = os.getenv("SALESFORCE_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = SalesforcePlugin(**cfg_dict)
    search = "FIND {admin} IN ALL FIELDS RETURNING Account(Id, Name)"
    ret = ins.execute_sosl(search)
    print(ret)
    assert ret != ""


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_execute_sosl():
    cfg = os.getenv("SALESFORCE_BASE_CONFIG")
    cfg_dict = json.loads(cfg)
    ins = SalesforcePlugin(**cfg_dict)
    query = "SELECT Id, Name FROM Account"
    ret = ins.execute_soql(query)
    print(ret)
    assert ret != ""

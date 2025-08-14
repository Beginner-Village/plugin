import pytest
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from pathlib import Path
from hiagent_plugin_jira_toolkit import JiraToolkitPlugin

load_dotenv("../../../.env")


# @pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_projects():
    plugin = JiraToolkitPlugin(
        os.getenv("TOOLKIT_JIRA_USERNAME"),
        os.getenv("TOOLKIT_JIRA_INSTANCE_URL"),
        os.getenv("TOOLKIT_JIRA_CLOUD") == "True",
        os.getenv("TOOLKIT_JIRA_API_TOKEN"),
    )
    result = plugin.projects()
    print("result", result)
    assert result != ""


def test_create_issue():
    plugin = JiraToolkitPlugin(
        os.getenv("TOOLKIT_JIRA_USERNAME"),
        os.getenv("TOOLKIT_JIRA_INSTANCE_URL"),
        os.getenv("TOOLKIT_JIRA_CLOUD") == "True",
        os.getenv("TOOLKIT_JIRA_API_TOKEN"),
    )
    query = """
{
  "project": {
    "id": "10001"
  },
  "issuetype": {
    "id": "10006"
  },
  "summary": "aa",
  "description": "this is from test case",
  "labels": [],
  "reporter": {
    "id": "712020:cd4a3ab8-4c8f-4cfb-aae5-62c81c1aa025"
  },
  "issuerestriction": {
    "projectrole": []
  },
  "customfield_10021": []
}
    """
    result = plugin.create_issue(query)
    print("result", result)
    assert result != ""


def test_jql():
    plugin = JiraToolkitPlugin(
        os.getenv("TOOLKIT_JIRA_USERNAME"),
        os.getenv("TOOLKIT_JIRA_INSTANCE_URL"),
        os.getenv("TOOLKIT_JIRA_CLOUD") == "True",
        os.getenv("TOOLKIT_JIRA_API_TOKEN"),
    )
    query = """assignee = currentUser()"""
    result = plugin.jql(query)
    print("result", result)
    assert result != ""



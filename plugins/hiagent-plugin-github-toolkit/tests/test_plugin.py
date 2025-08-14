import pytest
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from pathlib import Path
from hiagent_plugin_github_toolkit import GithubToolkitPlugin

load_dotenv("../../../.env")


# @pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_get_issues():
    plugin = GithubToolkitPlugin(os.getenv("TOOLKIT_GITHUB_APP_ID"), os.getenv("TOOLKIT_GITHUB_APP_PRIVATE_KEY"))
    result = plugin.get_issues(os.getenv("TOOLKIT_GITHUB_REPOSITORY"))
    print("\nresult", result)
    assert result != ""


# @pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_get_issue():
    plugin = GithubToolkitPlugin(os.getenv("TOOLKIT_GITHUB_APP_ID"), os.getenv("TOOLKIT_GITHUB_APP_PRIVATE_KEY"))
    result = plugin.get_issue(os.getenv("TOOLKIT_GITHUB_REPOSITORY"), 1)
    print("\nresult", result)
    assert result != ""


# @pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_read_file():
    plugin = GithubToolkitPlugin(os.getenv("TOOLKIT_GITHUB_APP_ID"), os.getenv("TOOLKIT_GITHUB_APP_PRIVATE_KEY"))
    result = plugin.read_file(os.getenv("TOOLKIT_GITHUB_REPOSITORY"), "toolkit1", "httpbin.yaml")
    print("\nresult", result)
    assert result != ""


def test_create_file():
    plugin = GithubToolkitPlugin(os.getenv("TOOLKIT_GITHUB_APP_ID"), os.getenv("TOOLKIT_GITHUB_APP_PRIVATE_KEY"))
    result = plugin.create_file(os.getenv("TOOLKIT_GITHUB_REPOSITORY"), "toolkit", "httpbin4.yaml", "created by github toolkit")
    print("\nresult", result)
    assert result != ""


def test_delete_file():
    plugin = GithubToolkitPlugin(os.getenv("TOOLKIT_GITHUB_APP_ID"), os.getenv("TOOLKIT_GITHUB_APP_PRIVATE_KEY"))
    result = plugin.delete_file(os.getenv("TOOLKIT_GITHUB_REPOSITORY"), "toolkit", "httpbin3.yaml")
    print("\nresult", result)
    assert result != ""


def test_update_file():
    plugin = GithubToolkitPlugin(os.getenv("TOOLKIT_GITHUB_APP_ID"), os.getenv("TOOLKIT_GITHUB_APP_PRIVATE_KEY"))
    result = plugin.update_file(
        os.getenv("TOOLKIT_GITHUB_REPOSITORY"),
        "toolkit",
        "httpbin4.yaml",
        "updated content",
    )
    print("\nresult", result)
    assert result != ""


def test_create_pull_request():
    plugin = GithubToolkitPlugin(os.getenv("TOOLKIT_GITHUB_APP_ID"), os.getenv("TOOLKIT_GITHUB_APP_PRIVATE_KEY"))
    result = plugin.create_pull_request(os.getenv("TOOLKIT_GITHUB_REPOSITORY"), "toolkit", "main", "github toolkit test",  "toolkit description")
    print("\nresult", result)
    assert result != ""

# @pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_comment_on_issue():
    from datetime import datetime

    # 获取当前日期和时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    plugin = GithubToolkitPlugin(os.getenv("TOOLKIT_GITHUB_APP_ID"), os.getenv("TOOLKIT_GITHUB_APP_PRIVATE_KEY"))
    result = plugin.comment_on_issue(
        os.getenv("TOOLKIT_GITHUB_REPOSITORY"),
        1,
        f"test_comment_on_issue {now}")
    print("\nresult", result)
    assert result != ""


class TreeNode:
    def __init__(self, value=0, parent=None):
        self.value = value
        self.parent = parent

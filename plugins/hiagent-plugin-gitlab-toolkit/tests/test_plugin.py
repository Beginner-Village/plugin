import pytest
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from pathlib import Path
from hiagent_plugin_gitlab_toolkit import GitlabToolkitPlugin

load_dotenv("../../../.env")


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_get_issues():
    plugin = GitlabToolkitPlugin(os.getenv("TOOLKIT_GITLAB_URL"), os.getenv("TOOLKIT_GITLAB_PERSONAL_ACCESS_TOKEN"))
    result = plugin.get_issues(os.getenv("TOOLKIT_GITLAB_REPOSITORY"))
    print("\nresult", result)
    assert result != ""


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_get_issue():
    plugin = GitlabToolkitPlugin(os.getenv("TOOLKIT_GITLAB_URL"), os.getenv("TOOLKIT_GITLAB_PERSONAL_ACCESS_TOKEN"))
    result = plugin.get_issue(os.getenv("TOOLKIT_GITLAB_REPOSITORY"), 1)
    print("\nresult", result)
    assert result != ""


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_read_file():
    plugin = GitlabToolkitPlugin(os.getenv("TOOLKIT_GITLAB_URL"), os.getenv("TOOLKIT_GITLAB_PERSONAL_ACCESS_TOKEN"))
    result = plugin.read_file(os.getenv("TOOLKIT_GITLAB_REPOSITORY"), "master", "readme.md")
    print("\nresult", result)
    assert result != ""


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_create_file():
    plugin = GitlabToolkitPlugin(os.getenv("TOOLKIT_GITLAB_URL"), os.getenv("TOOLKIT_GITLAB_PERSONAL_ACCESS_TOKEN"))
    result = plugin.create_file(os.getenv("TOOLKIT_GITLAB_REPOSITORY"),
                                "chore/gitlab-toolkit-test-01", "readme3.md", "create in test")
    print("\nresult", result)
    assert result != ""


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_delete_file():
    plugin = GitlabToolkitPlugin(os.getenv("TOOLKIT_GITLAB_URL"), os.getenv("TOOLKIT_GITLAB_PERSONAL_ACCESS_TOKEN"))
    result = plugin.delete_file(os.getenv("TOOLKIT_GITLAB_REPOSITORY"),
                                "chore/gitlab-toolkit-test-01", "readme2.md")
    print("\nresult", result)
    assert result != ""


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_update_file():
    plugin = GitlabToolkitPlugin(os.getenv("TOOLKIT_GITLAB_URL"), os.getenv("TOOLKIT_GITLAB_PERSONAL_ACCESS_TOKEN"))
    result = plugin.update_file(
        os.getenv("TOOLKIT_GITLAB_REPOSITORY"),
        "chore/gitlab-toolkit-test-01",
        "readme3.md",
        "updated content",
    )
    print("\nresult", result)
    assert result != ""


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_create_pull_request():
    plugin = GitlabToolkitPlugin(os.getenv("TOOLKIT_GITLAB_URL"), os.getenv("TOOLKIT_GITLAB_PERSONAL_ACCESS_TOKEN"))
    result = plugin.create_pull_request(
        os.getenv("TOOLKIT_GITLAB_REPOSITORY"),
        "chore/gitlab-toolkit-test-01",
        "chore/gitlab-toolkit-test",
        "merge test",
        "merge test description"
    )
    print("\nresult", result)
    assert result != ""


@pytest.mark.skipif(os.getenv("PYTEST_LOCAL") is None, reason="local only")
def test_comment_on_issue():
    from datetime import datetime

    # 获取当前日期和时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    plugin = GitlabToolkitPlugin(os.getenv("TOOLKIT_GITLAB_URL"), os.getenv("TOOLKIT_GITLAB_PERSONAL_ACCESS_TOKEN"))
    result = plugin.comment_on_issue(
        os.getenv("TOOLKIT_GITLAB_REPOSITORY"),
        2,
        f"test_comment_on_issue {now}")
    print("\nresult", result)
    assert result != ""


def test_icon_uri():
    uri = GitlabToolkitPlugin._icon_uri()
    print(uri)
    parsed_uri = urlparse(uri)
    assert parsed_uri.scheme == "file"
    assert Path(parsed_uri.path).is_file()


class TreeNode:
    def __init__(self, value=0, parent=None):
        self.value = value
        self.parent = parent

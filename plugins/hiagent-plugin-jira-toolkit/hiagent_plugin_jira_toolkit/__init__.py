import os
from pathlib import Path
from typing import Annotated, Dict, Any, List
from pydantic import Field, BaseModel

from langchain_community.utilities.jira import JiraAPIWrapper
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory, setup_ssrf_proxy_env

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


class IssueResult(BaseModel):
    id: str
    key: str


class IssueResults(BaseModel):
    issues: Annotated[
        str, Field(description="A plaintext report containing the number of issues and each issue's title and number.")]


class ActionResult(BaseModel):
    result: Annotated[str, Field(description="A success or failure message.")]


class JqlResult(BaseModel):
    result: Annotated[str, Field(description="")]


class ProjectResult(BaseModel):
    id: Annotated[str, Field(description="Project id.")]
    key: Annotated[str, Field(description="Project key.")]
    name: Annotated[str, Field(description="Project name.")]
    projectTypeKey: Annotated[str, Field(description="Project type key.")]
    style: Annotated[str, Field(description="Project style.")]


@set_meta(cn_name="JiraToolkit", en_name="jira-toolkit")
class JiraToolkitPlugin(BasePlugin):
    """Jira 是 Atlassian 提供的一款流行的项目管理和问题跟踪软件，广泛用于敏捷团队的软件开发流程中，以帮助团队规划、跟踪和管理项目。"""
    hiagent_tools = ["projects", "create_issue", "jql"]
    hiagent_category = BuiltinCategory.Productivity

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def __init__(self,
        username: Annotated[str, Field(description="")],
        instance_url: Annotated[str, Field(description="The url to be used in the request.")],
        cloud: Annotated[bool, Field(description="Specify if using Atlassian Cloud. Defaults to False.")],
        api_token: Annotated[str, SecretField(
                    description="https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/")],
    ):
        self.username = username
        self.instance_url = instance_url
        self.api_token = api_token
        self.cloud = cloud
        setup_ssrf_proxy_env()

        values = {
            "jira_api_token": self.api_token,
            "jira_username": self.username,
            "jira_instance_url": self.instance_url,
            "jira_cloud": str(self.cloud),
        }

        self.jiraAPIWrapper = JiraAPIWrapper(**values)  # type: ignore

    def projects(self) -> List[ProjectResult]:
        """
        Returns all projects which are visible for the currently logged-in user.
        If no user is logged in, it returns the list of projects that are visible when using anonymous access.
        """
        projects = self.jiraAPIWrapper.jira.projects()
        rets = []
        for project in projects:
            ret = ProjectResult(
                id=project["id"],
                key=project["key"],
                name=project["name"],
                projectTypeKey=project["projectTypeKey"],
                style=project["style"],
            )
            rets.append(ret)
        return rets


    def create_issue(self,
        fields: Annotated[str, Field(description="JSON data, mandatory keys are issuetype, summary and project.")],
    ) -> IssueResult:
        """
        Creates an issue or a sub-task from a JSON representation
        """
        try:
            import json
        except ImportError:
            raise ImportError(
                "json is not installed. Please install it with `pip install json`"
            )
        params = json.loads(fields)
        ret = self.jiraAPIWrapper.jira.issue_create(fields=dict(params))
        return IssueResult(id=ret["id"], key=ret["key"])

    def jql(self,
            jql: Annotated[str, Field(description="JQL query string")],
    ) -> JqlResult:
        """
        Get issues from jql search result with all related fields
        """

        ret = self.jiraAPIWrapper.jira.jql(jql)
        return JqlResult(result=str(ret))
import os
from pathlib import Path
from typing import Annotated, Dict, Any, List, Optional
from pydantic import Field, BaseModel

from langchain_community.utilities.gitlab import GitLabAPIWrapper
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory, setup_ssrf_proxy_env

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

class IssueResult(BaseModel):
    title: str
    description: str
    comments: str | None = None


class GitLabAPIWrapperX(GitLabAPIWrapper):
    # GitLabAPIWrapper 缺少 gitlab_url 字段，通过 values 传参校验会失败
    gitlab_url: Optional[str] = None


class IssueResults(BaseModel):
    issues: Annotated[
        str, Field(description="A plaintext report containing the number of issues and each issue's title and number.")]


class ActionResult(BaseModel):
    result: Annotated[str, Field(description="A success or failure message.")]


class ReadFileResult(BaseModel):
    content: Annotated[str, Field(description="file content.")]


@set_meta(cn_name="GitlabToolkit", en_name="gitlab-toolkit")
class GitlabToolkitPlugin(BasePlugin):
    """GitLab是一个提供代码仓库管理、代码审查、项目管理和CI/CD（持续集成/持续部署）等功能的一体化开发平台。"""
    hiagent_tools = ["get_issue", "get_issues", "comment_on_issue", "read_file", "create_file", "update_file", "delete_file", "create_pull_request"]
    hiagent_category = BuiltinCategory.Productivity

    def __init__(self,
        url: Annotated[str, Field(description="The URL hosted Gitlab, eg: https://gitlab.example.org")],
        personal_access_token: Annotated[str, SecretField()],
    ):
        self.personal_access_token = personal_access_token
        self.url = url
        setup_ssrf_proxy_env()

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def get_issues(self,
        repository: Annotated[str, Field(
        description="The name of the Gitlab repository. Must follow the format {username}/{repo-name}.")],
    ) -> IssueResults:
        """
        Fetches all open issues from the repo excluding pull requests
        """

        values = {
            "gitlab_url": self.url,
            "gitlab_personal_access_token": self.personal_access_token,
            "gitlab_repository": repository,
        }
        issues = GitLabAPIWrapperX(**values).get_issues()
        ret = IssueResults(issues=issues)
        return ret

    def get_issue(self,
        repository: Annotated[str, Field(
        description="The name of the Gitlab repository. Must follow the format {username}/{repo-name}.")],
        issue_number: Annotated[int, Field(description="The number for the gitlab issue.")],
    ) -> IssueResult:
        """
        Fetches a specific issue and its first 10 comments
        """

        values = {
            "gitlab_url": self.url,
            "gitlab_personal_access_token": self.personal_access_token,
            "gitlab_repository": repository,
        }
        issue_dict = GitLabAPIWrapperX(**values).get_issue(issue_number)
        ret = IssueResult(
            title=issue_dict["title"],
            description=issue_dict["body"],
            comments=issue_dict["comments"],
        )
        return ret

    def comment_on_issue(self,
        repository: Annotated[str, Field(description="The name of the Gitlab repository. Must follow the format {username}/{repo-name}.")],
        issue_number: int,
        comment: str
    ) -> ActionResult:
        """
        Adds a comment to a gitlab issue
        """
        values = {
            "gitlab_url": self.url,
            "gitlab_personal_access_token": self.personal_access_token,
            "gitlab_repository": repository,
        }
        gitlab_repo_instance = GitLabAPIWrapperX(**values).gitlab_repo_instance
        try:
            issue = gitlab_repo_instance.issues.get(issue_number)
            issue.notes.create({"body": comment})
            ret = ActionResult(result="Commented on issue " + str(issue_number))
            return ret
        except Exception as e:
            ret = ActionResult(result="Unable to make comment due to error:\n" + str(e))
            return ret

    def read_file(self,
        repository: Annotated[str, Field(description="The name of the Gitlab repository. Must follow the format {username}/{repo-name}.")],
        branch: Annotated[str, Field(description="The branch of the Gitlab repository.")],
        file_path: str
    ) -> ReadFileResult:
        """
        Reads a file from the gitlab repo
        """

        values = {
            "gitlab_url": self.url,
            "gitlab_personal_access_token": self.personal_access_token,
            "gitlab_repository": repository,
            "gitlab_branch": branch,
        }
        file_content = GitLabAPIWrapperX(**values).read_file(file_path)

        return ReadFileResult(content=file_content)

    def create_file(self, repository: Annotated[str, Field(description="The name of the Gitlab repository. Must follow the format {username}/{repo-name}.")],
        branch: Annotated[str, Field(description="The branch of the Gitlab repository.")],
        file_path: str,
        file_content: Annotated[str, Field(description="The new file contents.")]
    ) -> ActionResult:
        """
        Creates a new file on the gitlab repo
        """
        values = {
            "gitlab_url": self.url,
            "gitlab_personal_access_token": self.personal_access_token,
            "gitlab_repository": repository,
            "gitlab_branch": branch,
        }
        gitlab_repo_instance = GitLabAPIWrapperX(**values).gitlab_repo_instance

        try:
            gitlab_repo_instance.files.get(file_path, branch)
            return ActionResult(result="File already exists at " + file_path + ". Use update_file instead")
        except Exception:
            data = {
                "branch": branch,
                "commit_message": "Create " + file_path,
                "file_path": file_path,
                "content": file_content,
            }

            gitlab_repo_instance.files.create(data)
            return ActionResult(result="Created file " + file_path)

    def delete_file(self,
        repository: Annotated[str, Field(description="The name of the Gitlab repository. Must follow the format {username}/{repo-name}.")],
        branch: Annotated[str, Field(description="The branch of the Gitlab repository.")],
        file_path: str
    ) -> ActionResult:
        """
        Deletes a file from the repo
        """
        values = {
            "gitlab_url": self.url,
            "gitlab_personal_access_token": self.personal_access_token,
            "gitlab_repository": repository,
            "gitlab_branch": branch,
        }
        ret = GitLabAPIWrapperX(**values).delete_file(file_path)
        return ActionResult(result=ret)


    def update_file(self,
        repository: Annotated[str, Field(description="The name of the Gitlab repository. Must follow the format {username}/{repo-name}.")],
        branch: Annotated[str, Field(description="The branch of the Gitlab repository.")],
        file_path: str,
        file_content: Annotated[str, Field(description="The new file contents.")]
    ) -> ActionResult:
        """
        Updates a file with new content.
        """

        values = {
            "gitlab_url": self.url,
            "gitlab_personal_access_token": self.personal_access_token,
            "gitlab_repository": repository,
            "gitlab_branch": branch,
        }

        commit = {
            "branch": branch,
            "commit_message": "Create " + file_path,
            "actions": [
                {
                    "action": "update",
                    "file_path": file_path,
                    "content": file_content,
                }
            ],
        }
        gitlab_repo_instance = GitLabAPIWrapperX(**values).gitlab_repo_instance
        try:
            gitlab_repo_instance.commits.create(commit)
            return ActionResult(result="Updated file " + file_path)
        except Exception as e:
            return ActionResult(result="Unable to update file due to error:\n" + str(e))

    def create_pull_request(self,
        repository: Annotated[str, Field(description="The name of the Gitlab repository. Must follow the format {username}/{repo-name}.")],
        source_branch: Annotated[str, Field(description="The source branch of the pull request.")],
        target_branch: Annotated[str, Field(description="The target branch of the pull request.")],
        title: Annotated[str, Field(description="The title of the pull request.")],
        description: Annotated[str, Field(description="The description of the pull request.")],
    ) -> ActionResult:
        """
        Makes a pull request to the target branch
        """
        values = {
            "gitlab_url": self.url,
            "gitlab_personal_access_token": self.personal_access_token,
            "gitlab_repository": repository,
            "gitlab_branch": source_branch,
            "gitlab_base_branch": target_branch,
        }
        gitlab_repo_instance = GitLabAPIWrapperX(**values).gitlab_repo_instance

        if source_branch == target_branch:
            return ActionResult(result="Cannot make a pull request because commits are already in the target branch")
        else:
            try:
                pr = gitlab_repo_instance.mergerequests.create(
                    {
                        "source_branch": source_branch,
                        "target_branch": target_branch,
                        "title": title,
                        "description": description,
                        # "labels": ["created-by-agent"],
                    }
                )
                return ActionResult(result="Successfully created PR number " + str(pr.iid))
            except Exception as e:
                return ActionResult(result="Unable to make pull request due to error:\n" + str(e))
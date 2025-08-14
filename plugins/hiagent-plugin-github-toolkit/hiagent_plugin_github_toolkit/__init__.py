import os
from pathlib import Path
from typing import Annotated, Dict, Any, List
from pydantic import Field, BaseModel

from langchain_community.utilities.github import GitHubAPIWrapper
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


class IssueResult(BaseModel):
    title: str
    description: str
    comments: str | None = None


class IssueResults(BaseModel):
    issues: Annotated[
        str, Field(description="A plaintext report containing the number of issues and each issue's title and number.")]


class ActionResult(BaseModel):
    result: Annotated[str, Field(description="A success or failure message.")]


class ReadFileResult(BaseModel):
    content: Annotated[str, Field(description="file content.")]


@set_meta(cn_name="GithubToolkit", en_name="github-toolkit")
class GithubToolkitPlugin(BasePlugin):
    """GitHub 是一个开发者平台，允许开发者创建、存储、管理和分享他们的代码。"""
    hiagent_tools = ["get_issue", "get_issues", "comment_on_issue", "read_file",
                     "delete_file", "create_file", "update_file", "create_pull_request"]
    hiagent_category = BuiltinCategory.Productivity

    def __init__(self,
        app_id: Annotated[str, Field(description="A six digit number found in your app's general settings")],
        app_private_key: Annotated[str, SecretField()],
    ):
        self.app_private_key = app_private_key
        self.app_id = app_id

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def get_issues(self,
        repository: Annotated[str, Field(
        description="The name of the Github repository. Must follow the format {username}/{repo-name}.")],
    ) -> IssueResults:
        """
        Fetches all open issues from the repo excluding pull requests
        """

        values = {
            "github_app_id": self.app_id,
            "github_app_private_key": self.app_private_key,
            "github_repository": repository,
        }
        issues = GitHubAPIWrapper(**values).get_issues()
        ret = IssueResults(issues=issues)
        return ret

    def get_issue(self,
        repository: Annotated[str, Field(
        description="The name of the Github repository. Must follow the format {username}/{repo-name}.")],
        issue_number: Annotated[int, Field(description="The number for the github issue.")],
    ) -> IssueResult:
        """
        Fetches a specific issue and its first 10 comments
        """

        values = {
            "github_app_id": self.app_id,
            "github_app_private_key": self.app_private_key,
            "github_repository": repository,
        }
        issue_dict = GitHubAPIWrapper(**values).get_issue(issue_number)
        ret = IssueResult(
            title=issue_dict["title"],
            description=issue_dict["body"],
            comments=issue_dict["comments"],
        )
        return ret

    def comment_on_issue(self,
        repository: Annotated[str, Field(
        description="The name of the Github repository. Must follow the format {username}/{repo-name}.")],
        issue_number: int,
        comment: str
    ) -> ActionResult:
        """
        Adds a comment to a github issue
        """

        values = {
            "github_app_id": self.app_id,
            "github_app_private_key": self.app_private_key,
            "github_repository": repository,
        }
        instance = GitHubAPIWrapper(**values).github_repo_instance
        try:
            issue = instance.get_issue(number=issue_number)
            issue.create_comment(comment)
            ret = ActionResult(result="Commented on issue " + str(issue_number))
            return ret
        except Exception as e:
            ret = ActionResult(result="Unable to make comment due to error:\n" + str(e))
            return ret

    def read_file(self,
        repository: Annotated[str, Field(
        description="The name of the Github repository. Must follow the format {username}/{repo-name}.")],
        branch: Annotated[str, Field(description="The branch of the Github repository.")],
        file_path: str
    ) -> ReadFileResult:
        """
        Reads a file from the github repo
        """

        values = {
            "github_app_id": self.app_id,
            "github_app_private_key": self.app_private_key,
            "github_repository": repository,
            "active_branch": branch,
        }
        file_content = GitHubAPIWrapper(**values).read_file(file_path)

        return ReadFileResult(content=file_content)

    def create_file(self, repository: Annotated[
        str, Field(description="The name of the Github repository. Must follow the format {username}/{repo-name}.")],
                    branch: Annotated[str, Field(description="The branch of the Github repository.")],
                    file_path: str,
                    file_content: Annotated[str, Field(description="The new file contents.")]
                    ) -> ActionResult:
        """
        Creates a new file on the github repo
        """

        values = {
            "github_app_id": self.app_id,
            "github_app_private_key": self.app_private_key,
            "github_repository": repository,
            "active_branch": branch,
        }
        instance = GitHubAPIWrapper(**values).github_repo_instance

        try:
            try:
                file = instance.get_contents(
                    file_path, ref=branch
                )
                if file:
                    return ActionResult(result="File already exists at `{file_path}` "
                                               f"on branch `{branch}`. You must use "
                                               "`update_file` to modify it.")
            except Exception:
                # expected behavior, file shouldn't exist yet
                pass

            instance.create_file(
                path=file_path,
                message="Create " + file_path,
                content=file_content,
                branch=branch,
            )
            return ActionResult(result="Created file " + file_path)
        except Exception as e:
            return ActionResult(result="Unable to make file due to error:\n" + str(e))

    # 这个方法有问题，似乎只能删除 default 分支的文件，暂未启用
    def delete_file(self,
                    repository: Annotated[str, Field(
                        description="The name of the Github repository. Must follow the format {username}/{repo-name}.")],
                    branch: Annotated[str, Field(description="The branch of the Github repository.")],
                    file_path: str
                    ) -> ActionResult:
        """
        Deletes a file from the repo
        """

        values = {
            "github_app_id": self.app_id,
            "github_app_private_key": self.app_private_key,
            "github_repository": repository,
            "active_branch": branch,
        }
        ret = GitHubAPIWrapper(**values).delete_file(file_path)
        return ActionResult(result=ret)

    def update_file(self,
                    repository: Annotated[str, Field(
                        description="The name of the Github repository. Must follow the format {username}/{repo-name}.")],
                    branch: Annotated[str, Field(description="The branch of the Github repository.")],
                    file_path: str,
                    file_content: Annotated[str, Field(description="The new file contents.")]
                    ) -> ActionResult:
        """
        Updates a file with new content.
        """

        values = {
            "github_app_id": self.app_id,
            "github_app_private_key": self.app_private_key,
            "github_repository": repository,
            "active_branch": branch,
        }

        instance = GitHubAPIWrapper(**values).github_repo_instance
        try:
            old_file_content = self.read_file(repository, branch, file_path)

            if file_content == old_file_content:
                return ActionResult(result="File content was not updated because old content was not found.")

            instance.update_file(
                path=file_path,
                message="Update " + str(file_path),
                content=file_content,
                branch=branch,
                sha=instance.get_contents(
                    file_path, ref=branch
                ).sha,
            )
            return ActionResult(result="Updated file " + str(file_path))
        except Exception as e:
            return ActionResult(result="Unable to update file due to error:\n" + str(e))

    def create_pull_request(self,
                            repository: Annotated[str, Field(
                                description="The name of the Github repository. Must follow the format {username}/{repo-name}.")],
                            source_branch: Annotated[str, Field(description="The source branch of the pull request.")],
                            target_branch: Annotated[str, Field(description="The target branch of the pull request.")],
                            title: Annotated[str, Field(description="The title of the pull request.")],
                            description: Annotated[str, Field(description="The description of the pull request.")],
                            ) -> ActionResult:
        """
        Makes a pull request to the target branch
        """

        values = {
            "github_app_id": self.app_id,
            "github_app_private_key": self.app_private_key,
            "github_repository": repository,
            "active_branch": source_branch,
            "github_base_branch": target_branch
        }
        instance = GitHubAPIWrapper(**values).github_repo_instance

        if source_branch == target_branch:
            return ActionResult(result="Cannot make a pull request because commits are already in the target branch")
        else:
            try:
                # GitHubAPIWrapper().create_pull_request()
                pr = instance.create_pull(
                    title=title,
                    body=description,
                    head=source_branch,
                    base=target_branch,
                )
                return ActionResult(result="Successfully created PR number " + str(pr.number))
            except Exception as e:
                return ActionResult(result="Unable to make pull request due to error:\n" + str(e))

import os
from typing import Annotated
from pathlib import Path
from pydantic import Field
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory
from simple_salesforce import Salesforce, SalesforceError

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


@set_meta(cn_name="Salesforce")
class SalesforcePlugin(BasePlugin):
    """Salesforce"""
    hiagent_tools = ["execute_sosl", "execute_soql"]
    hiagent_category = BuiltinCategory.WebSearch

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def __init__(self,
        sf_username: Annotated[str, Field(description="申请说明: <https://help.salesforce.com/s/articleView?id=sf.rss_login_self_register.htm&type=5>")],
        sf_password: Annotated[str, SecretField(description="申请说明: <https://help.salesforce.com/s/articleView?id=sf.rss_login_self_register.htm&type=5>")],
        sf_security_token: Annotated[str, SecretField(description="申请说明: <https://help.salesforce.com/s/articleView?id=xcloud.user_security_token.htm&language=en_US&type=5>")],
    ) -> None:

        self.sf_username = sf_username
        self.sf_password = sf_password
        self.sf_security_token = sf_security_token
        self.sf = Salesforce(
            username=self.sf_username,
            password=self.sf_password,
            security_token=self.sf_security_token,
        )

    def execute_sosl(
            self,
            search: Annotated[str, Field(description="搜索项")],
    ) -> str:

        try:
            res = self.sf.search(search)
        except SalesforceError as err:
            return f"Error running SOSL query: {err}"
        return str(res)

    def execute_soql(
            self,
            query: Annotated[str, Field(description="搜索项")],
    ) -> str:

        try:
            res = self.sf.query_all(query)
        except SalesforceError as err:
            return f"Error running SOQL query: {err}"
        return str(res)

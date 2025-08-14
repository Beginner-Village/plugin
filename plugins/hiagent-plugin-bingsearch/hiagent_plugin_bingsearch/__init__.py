
from typing import Any, Optional, List, Dict, Annotated
import os
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_community.utilities.bing_search import BingSearchAPIWrapper, DEFAULT_BING_SEARCH_ENDPOINT
from hiagent_plugin_sdk import BasePlugin, ConfigValidateMixin, set_meta, SecretField, BuiltinCategory, setup_ssrf_proxy_env

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

class BingSearchResults(BaseModel):
    snippet: str
    title: str
    link: str

@set_meta(cn_name="Bing", en_name="Bing")
class BingSearchPlugin(BasePlugin, ConfigValidateMixin):
    """Bing Search"""
    hiagent_tools = ["search", "search_results"]
    hiagent_category = BuiltinCategory.WebSearch

    def __init__(
        self,
        api_key: Annotated[str, SecretField(description="申请说明: <https://www.microsoft.com/cognitive-services/en-us/bing-web-search-api>")],
        search_url: str = DEFAULT_BING_SEARCH_ENDPOINT
    ) -> None:
        self.api_key = api_key
        self.search_url = search_url
        setup_ssrf_proxy_env()

    def _validate(self):
        self.search_results("test", 1)

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def search(self, query: str) -> str:
        """Search for the query on Bing."""
        bing_search = BingSearchAPIWrapper(
            bing_subscription_key=self.api_key, bing_search_url=self.search_url)
        return bing_search.run(query)

    def search_results(self, query: str, num_results: int = 10) -> List[BingSearchResults]:
        """Search for the query on Bing and return the results."""
        bing_search = BingSearchAPIWrapper(
            bing_subscription_key=self.api_key, bing_search_url=self.search_url, k=num_results)
        ret = bing_search.results(query, num_results)
        return [BingSearchResults(**r) for r in ret]

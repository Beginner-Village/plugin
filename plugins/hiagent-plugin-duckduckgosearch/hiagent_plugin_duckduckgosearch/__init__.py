
from typing import Any, Optional, List, Dict, Annotated, Literal
import os
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper # type: ignore
from hiagent_plugin_sdk import BasePlugin, set_meta, BuiltinCategory

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


class SearchResults(BaseModel):
    snippet: str
    title: str
    link: str
    date: str | None = Field(None)
    source: str | None = Field(None)


@set_meta(cn_name="DuckDuckGoSearch")
class DuckDuckGoSearchPlugin(BasePlugin):
    """DuckDuckGo Search"""
    hiagent_tools = ["search", "search_results"]
    hiagent_category = BuiltinCategory.WebSearch

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def search(self, query: str) -> str:
        """Run query through DuckDuckGo and return concatenated results."""
        api = DuckDuckGoSearchAPIWrapper()
        return api.run(query)

    def search_results(self,
        query: str,
        source: Annotated[Literal["text", "news"], Field(title="search source", description="text or news")] = "text",
        max_results: int = 5,
    ) -> List[SearchResults]:
        """Run query through DuckDuckGo and return metadata"""
        api = DuckDuckGoSearchAPIWrapper()
        ret_list = api.results(query, max_results=max_results, source=source)
        import json
        print(json.dumps(ret_list, indent=2, ensure_ascii=False))
        return [SearchResults(**r) for r in ret_list]

import os
from pathlib import Path
from typing import Annotated, Optional

from semanticscholar import SemanticScholar # type: ignore
from hiagent_plugin_sdk import BasePlugin, set_meta, BuiltinCategory
from pydantic import Field

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

doc_content_chars_max: Optional[int] = 4000

@set_meta(cn_name="SemanticScholar", en_name="SemanticScholar")
class SemanticScholarPlugin(BasePlugin):
    """Tool that searches the SemanticScholar API."""

    hiagent_tools = ["search"]
    hiagent_category = BuiltinCategory.Education

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def search(self,
        query: str,
        top_k_results: Annotated[int, Field(description="返回结果数量")] = 5,
        load_max_docs: Annotated[int, Field(description="最大加载文档数量")] = 10,
    ) -> str:
        client = SemanticScholar()
        documents = []
        raw_results = client.search_paper(query=query, limit=load_max_docs)
        for item in raw_results.items[:top_k_results]:
            authors = ", ".join(
                author["name"] for author in getattr(item, "authors", [])
            )
            documents.append(
                f"Published year: {getattr(item, 'year', None)}\n"
                f"Title: {getattr(item, 'title', None)}\n"
                f"Authors: {authors}\n"
                f"Abstract: {getattr(item, 'abstract', None)}\n"
            )

        if documents:
            return "\n\n".join(documents)[: doc_content_chars_max]
        else:
            return "No results found."
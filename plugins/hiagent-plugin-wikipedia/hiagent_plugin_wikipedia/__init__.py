
import os
from pathlib import Path
import wikipedia # type: ignore
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from hiagent_plugin_sdk import BasePlugin, set_meta, BuiltinCategory

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

WIKIPEDIA_MAX_QUERY_LENGTH = 300

@set_meta(cn_name="维基百科", en_name="Wikipedia")
class WikipediaPlugin(BasePlugin):
    """维基百科是一个由全世界的志愿者创建和编辑的免费在线百科全书。"""
    hiagent_tools = ["search"]
    hiagent_category = BuiltinCategory.WebSearch

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def search(self, query: str, lang: str = "en") -> str:
        """A tool for performing a Wikipedia search and extracting snippets and webpages. Input should be a search query."""
        return WikipediaAPIWrapper(wiki_client=wikipedia, lang=lang).run(query)


import os
from pathlib import Path
from typing import List
from langchain_community.tools.wikidata.tool import WikidataAPIWrapper
from hiagent_plugin_sdk import BasePlugin, set_meta, BuiltinCategory

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

WIKIPEDIA_MAX_QUERY_LENGTH = 300

@set_meta(cn_name="wikidata")
class WikidataPlugin(BasePlugin):
    """Tool that searches the Wikidata API."""
    hiagent_tools = ["search"]
    hiagent_category = BuiltinCategory.WebSearch

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def search(self, query: str) -> str:
        """Tool that searches the Wikidata API."""
        cli = WikidataAPIWrapper() # type: ignore
        return cli.run(query)

    # def search_doc(self, query: str) -> List[Document]:
    #     """Tool that searches the Wikidata API. return """
    #     cli = WikidataAPIWrapper()
    #     return cli.load(query)

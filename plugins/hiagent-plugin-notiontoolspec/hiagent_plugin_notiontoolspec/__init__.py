import os
from typing import Annotated
from pathlib import Path
from pydantic import Field
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

"""Notion tool spec."""

from typing import Any, Dict, List, Optional, Type

import requests
from llama_index.core.bridge.pydantic import BaseModel
from llama_index.core.tools.tool_spec.base import SPEC_FUNCTION_TYPE, BaseToolSpec
from llama_index.readers.notion import NotionPageReader

SEARCH_URL = "https://api.notion.com/v1/search"


class NotionLoadDataSchema(BaseModel):
    """Notion load data schema."""

    page_ids: Optional[List[str]] = None
    database_id: Optional[str] = None


class NotionSearchDataSchema(BaseModel):
    """Notion search data schema."""

    query: str
    direction: Optional[str] = None
    timestamp: Optional[str] = None
    value: Optional[str] = None
    property: Optional[str] = None
    page_size: int = 100


class ActionResult(BaseModel):
    result: Annotated[str, Field(description="")]


class SearchResult(BaseModel):
    object: str
    id: str
    created_time: Optional[str] = None
    last_edited_time: Optional[str] = None
    archived: Optional[bool] = None
    in_trash: Optional[bool] = None
    url: Optional[str] = None
    public_url: Optional[str] = None


@set_meta(cn_name="NotionToolSpec", en_name="notion-tool-spec")
class NotionToolSpecPlugin(BasePlugin, BaseToolSpec):
    """NotionToolSpec loads and updates documents from Notion. """

    hiagent_tools = ["load_data", "search_data"]
    hiagent_category = BuiltinCategory.Productivity

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def __init__(self, integration_token: Annotated[str, SecretField(description="https://www.notion.so/profile/integrations")]) -> None:
        """Initialize with parameters."""
        self.reader = NotionPageReader(integration_token=integration_token)

    def get_fn_schema_from_fn_name(
        self, fn_name: str, spec_functions: Optional[List[SPEC_FUNCTION_TYPE]] = None
    ) -> Optional[Type[BaseModel]]:
        """Return map from function name."""
        if fn_name == "load_data":
            return NotionLoadDataSchema
        elif fn_name == "search_data":
            return NotionSearchDataSchema
        else:
            raise ValueError(f"Invalid function name: {fn_name}")

    def load_data(self, page_id: Annotated[str, Field(description="Notion page id")]) -> ActionResult:
        """Loads content from a set of page id.Don't use this tool if you don't know the page id."""
        page_ids = [page_id]
        docs = self.reader.load_data(page_ids=page_ids)
        ret = "\n".join([doc.get_content() for doc in docs])
        return ActionResult(result=ret)

    def search_data(
        self,
        query: Annotated[str, Field(description="The text that the API compares page and database titles against.")],
        direction: Annotated[str, Field(description="The direction to sort. Possible values include ascending and descending.")] = "descending",
        timestamp: Annotated[str, Field(description="The name of the timestamp to sort against. Possible values include last_edited_time.")] = "last_edited_time",
        value: Annotated[str, Field(description="The value of the property to filter the results by. ")] = None,
        property: Annotated[str, Field(description="The name of the property to filter the results by.")] = None,
        page_size: Annotated[int, Field(description="The number of items from the full list to include in the response. Maximum: 100.")] = 100,
    ) -> List[SearchResult]:
        """
        Search a list of relevant pages.Contains metadata for each page (but not the page content).
        """
        payload: Dict[str, Any] = {
            "query": query,
            "page_size": page_size,
        }
        if direction is not None or timestamp is not None:
            payload["sort"] = {}
            if direction is not None:
                payload["sort"]["direction"] = direction
            if timestamp is not None:
                payload["sort"]["timestamp"] = timestamp

        if value is not None or property is not None:
            payload["filter"] = {}
            if value is not None:
                payload["filter"]["value"] = value
            if property is not None:
                payload["filter"]["property"] = property

        response = requests.post(SEARCH_URL, json=payload, headers=self.reader.headers)
        response_json = response.json()
        # return response_json["results"]
        rets = []
        for result in response_json["results"]:
            ret = SearchResult(
                object=result["object"],
                id=result["id"],
                created_time=result["created_time"],
                last_edited_time=result["last_edited_time"],
                archived=result["archived"],
                in_trash=result["in_trash"],
                url=result["url"],
                public_url=result["public_url"],
            )
            rets.append(ret)
        return rets

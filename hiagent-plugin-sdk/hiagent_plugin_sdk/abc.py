
from typing import List, Any, AsyncGenerator
from abc import ABC, abstractmethod
from hiagent_plugin_sdk.schema import Metadata

class AdapterRuntime(ABC):
    @classmethod
    @abstractmethod
    async def run_plugin_tool(self, tool: str, input: dict, cfg: dict) -> Any:
        pass

    @classmethod
    @abstractmethod
    async def run_plugin_validate(self, cfg: dict) -> None:
        pass

    @classmethod
    @abstractmethod
    async def run_plugin_tool_stream(self, tool: str, input: dict, cfg: dict) -> AsyncGenerator[Any, None]:
        pass

    @classmethod
    @abstractmethod
    def get_metadata(self) -> Metadata:
        pass

    @staticmethod
    def ping() -> str:
        return "pong"

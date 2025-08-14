from typing import List, Any, Callable, AsyncGenerator
import logging
import yaml
from functools import partial
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps

from pydantic import Field, BaseModel, RootModel, create_model

from hiagent_plugin_sdk.schema import Metadata, PackageInfo, ToolMetadata, complete_metadata, HttpError
from hiagent_plugin_sdk.utils import get_fn_schema
from hiagent_plugin_sdk.consts import *

logger = logging.getLogger(__name__)


class Plugin:
    meta_version = "v2"

    def __init__(self, name: str, cfg: type[BaseModel] | None = None) -> None:
        self.name = name
        self.cfg_model = cfg
        self._tools: List[ToolMetadata] = []
        self._config_validate_fn: Callable | None = None

    def config_validate_fn(self, fn):
        """
        decorator for config validate function:
        @plugin.config_validate_fn
        def config_validate_fn(cfg):
            ...
        """
        self._config_validate_fn = fn
        @wraps
        async def wrapper(*args, **kwargs):
            return await fn(*args, **kwargs)
        return wrapper

    def tool_fn(self, name: str | None = None):
        """
        decorator for tool function:
        @plugin.tool_fn()
        def tool_fn(input, cfg=None, stream=False):
            ...
        """
        async def decorator(fn):
            self._registry_tool_fn(fn)
            @wraps(fn)
            async def wrapper(*args, **kwargs):
                return await fn(*args, **kwargs)
            return wrapper
        return decorator

    def _registry_tool_fn(self, fn):
        # TODO
        ...

    async def arun_tool(self, tool_name: str, input: dict, cfg: dict | None = None, stream: bool = False) -> Any:
        """
        run tool function
        """
        for tool in self._tools:
            if tool.name == tool_name:
                if tool.entry_point is None:
                    raise ValueError(f"tool {tool_name} not implemented")
                return await tool.entry_point(input, cfg=cfg, stream=stream)
        raise ValueError(f"tool {tool_name} not found")


import asyncio
import logging
import traceback
import json
from typing import Any, List, AsyncGenerator
from functools import lru_cache, cache

from pydantic import BaseModel

from hiagent_plugin_sdk.v1 import BasePlugin
from hiagent_plugin_sdk.schema import Metadata
from hiagent_plugin_sdk import secretLogger

from app.schema.common import HttpException, HttpError
from app.config import PLUGIN_ENTRY_GROUP


logger = logging.getLogger(__name__)


class RunToolReq(BaseModel):
    plugin: str
    tool: str
    input: dict = {}
    config: dict | None = None
    action: str = "run_tool"

class RunToolStreamReq(BaseModel):
    plugin: str
    tool: str
    input: dict = {}
    config: dict | None = None
    stream: bool = True
    action: str = "run_tool_stream"

class RunPingReq(BaseModel):
    action: str = "run_ping"
    plugin: str

class RunValidateReq(BaseModel):
    plugin: str
    config: dict | None = None
    action: str = "run_validate"


class RunMetadataReq(BaseModel):
    plugin: str
    action: str = "run_metadata"

class RunPkgMetadataReq(BaseModel):
    action: str = "run_pkg_metadata"

class Resp(BaseModel):
    data: Any | None = None
    error: HttpError | None = None


class SockHandler:
    def _load_entry(self, plugin) -> type[BasePlugin]:
        import importlib
        import importlib.metadata
        entries = importlib.metadata.entry_points(
            name=plugin, group=PLUGIN_ENTRY_GROUP)
        if len(entries) == 0:
            raise HttpException(
                code="PluginEntryNotFound",
                message=f"plugin entry: {plugin} not found",
                http_code=404
            )
        # 3.12 不支持 index 索引 https://github.com/python/importlib_metadata/commit/5ca9bc7dcf73d72260486afb28dadf5e532cf657
        return list(entries)[0].load()

    def _list_entry(self) -> list[str]:
        import importlib.metadata
        entries = importlib.metadata.entry_points(group=PLUGIN_ENTRY_GROUP)
        return [entry.name for entry in entries]

    async def dispatch(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            await self._dispatch(reader, writer)
        except Exception as e:
            print(traceback.format_exc())
            http_err: HttpException = HttpException.from_exception(e)
            data = json.dumps({"error": {
                "code": http_err.code,
                "message": http_err.message,
                "data": http_err.data,
                "http_code": http_err.http_code
            }})
            writer.write(data.encode())
            writer.write_eof()
            await writer.drain()
            writer.close()

    async def _dispatch(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        resp = Resp()
        data = await reader.read()
        req = json.loads(data)
        action = req.get("action", None)
        stream = req.get("stream", False)
        if action is None:
            raise HttpException(
                code="InvalidRequest",
                message="action is required",
                http_code=400
            )
        if not hasattr(self, action):
            raise HttpException(
                code="ActionNotFound",
                message=f"invalid action: {action}",
                http_code=400
            )
        handle_fn = getattr(self, action)
        if not stream:
            ret = await handle_fn(req)
            resp.data = ret
            resp_raw = resp.model_dump_json()
            writer.write(resp_raw.encode())
            writer.write_eof()
            await writer.drain()
        else:
            async for ret in await handle_fn(req):
                resp.data = ret
                resp_raw = resp.model_dump_json()
                writer.write(resp_raw.encode())
                writer.write(b"\n")
                await writer.drain()
            writer.write_eof()
        writer.close()

    async def run_tool(self, data: dict) -> Any:
        req = RunToolReq(**data)
        secretLogger.info(f"run_tool: {req}")
        entry_cls: type[BasePlugin] = self._load_entry(req.plugin)
        return await entry_cls.run_plugin_tool(req.tool, req.input, req.config)

    async def run_tool_stream(self, data: dict) -> AsyncGenerator[Any, None]:
        req = RunToolReq(**data)
        secretLogger.info(f"run_tool_stream: {req}")
        entry_cls: type[BasePlugin] = self._load_entry(req.plugin)
        return entry_cls.run_plugin_tool_stream(req.tool, req.input, req.config)
        # if req.config is not None:
        #     ins: BasePlugin = entry_cls(**req.config)
        # else:
        #     ins = entry_cls()
        # return adapter.run_plugin_tool_stream(ins, req.tool, req.input)
        # return adapter.fake_run_plugin_tool_stream(ins, req.tool, req.input)

    async def run_validate(self, data: dict) -> None:
        req = RunValidateReq(**data)
        secretLogger.info(f"run_validate: {req}")
        entry_cls: type[BasePlugin] = self._load_entry(req.plugin)
        return await entry_cls.run_plugin_validate(req.config)

    async def run_metadata(self, data: dict) -> Metadata:
        req = RunMetadataReq(**data)
        logger.info(f"run_metadata: {req}")
        entry_cls: type[BasePlugin] = self._load_entry(req.plugin)
        return entry_cls.get_metadata()

    async def run_pkg_metadata(self, data: dict) -> List[Metadata]:
        req = RunPkgMetadataReq(**data)
        logger.info(f"run_pkg_metadata: {req}")
        entries = self._list_entry()
        if len(entries) ==0:
            raise HttpException(
                code="PluginNotFound",
                message=f"no plugin found",
                http_code=404
            )
        task = [self.run_metadata({"plugin": entry}) for entry in self._list_entry()]
        rets = await asyncio.gather(*task)
        return rets

    async def run_ping(self, data: dict) -> str:
        req = RunPingReq(**data)
        logger.info(f"run_ping: {req}")
        entry_cls: type[BasePlugin] = self._load_entry(req.plugin)
        return entry_cls.ping()
